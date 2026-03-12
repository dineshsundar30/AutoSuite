import os
import glob
import chromadb
from sentence_transformers import SentenceTransformer

class RepoIndexer:
    """
    Scans a repository for Robot files, keywords, locators, and python files,
    indexing them into ChromaDB for similarity search during analysis.
    """
    def __init__(self, repo_path: str, persist_directory: str = None):
        self.repo_path = os.path.abspath(repo_path)
        
        if not persist_directory:
            persist_directory = os.environ.get("CHROMA_DB_DIR", "./chroma_db")
            
        # Ensure the directory exists
        os.makedirs(persist_directory, exist_ok=True)
            
        # Initialize chroma client
        self.chroma_client = chromadb.PersistentClient(path=persist_directory)
        
        # Use sentence transformers to generate embeddings
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Get or create collection
        self.collection = self.chroma_client.get_or_create_collection(name="repo_knowledge")

    def _get_files_by_extension(self, extensions):
        matched_files = []
        for root, _, files in os.walk(self.repo_path):
            # Skip hidden directories like .git
            if '/.' in root or '\\.' in root:
                continue
                
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    matched_files.append(os.path.join(root, file))
        return matched_files

    def index_repository(self):
        """Scans the repo and indexes content into Vector DB."""
        print(f"Scanning repository: {self.repo_path}")
        
        files_to_index = self._get_files_by_extension(['.robot', '.resource', '.py'])
        documents = []
        metadatas = []
        ids = []
        
        for idx, file_path in enumerate(files_to_index):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Basic chunking: treat each file as a single document for now
                    # In a production system, we'd chunk by Robot keyword or Python function
                    if content.strip():
                        # Store relative paths
                        rel_path = os.path.relpath(file_path, self.repo_path)
                        
                        documents.append(content)
                        metadatas.append({"file_path": rel_path, "type": os.path.splitext(file_path)[1]})
                        ids.append(f"doc_{idx}")
            except Exception as e:
                print(f"Warning: Could not read {file_path}. {str(e)}")
                
        if documents:
            print(f"Generating embeddings for {len(documents)} files...")
            embeddings = self.embedding_model.encode(documents)
            
            print("Storing in ChromaDB...")
            self.collection.add(
                embeddings=embeddings.tolist(),
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            print("Indexing complete.")
        else:
            print("No valid files found to index.")

    def search_similar(self, query: str, n_results: int = 3):
        """Searches the repository index for context relevant to the given query."""
        query_embedding = self.embedding_model.encode([query])
        
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=n_results
        )
        
        context_items = []
        if results and results['documents'] and len(results['documents']) > 0:
            for i, doc in enumerate(results['documents'][0]):
                meta = results['metadatas'][0][i]
                context_items.append({
                    "file": meta['file_path'],
                    "content": doc,
                    "distance": results['distances'][0][i] if 'distances' in results else 0
                })
                
        return context_items

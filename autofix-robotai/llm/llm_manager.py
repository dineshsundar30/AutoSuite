import os
from langchain_community.llms import Ollama

class LLMManager:
    """
    Manages the connection and configuration for the local Ollama LLM.
    """
    def __init__(self, model_name="deepseek-coder", base_url=None):
        self.model_name = model_name
        
        # Use environment variable if base_url is not provided
        if not base_url:
            base_url = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            
        self.base_url = base_url
        self.llm = self._initialize_llm()

    def _initialize_llm(self):
        """Initializes the Ollama instance via langchain"""
        try:
            return Ollama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=0.1 # low temperature for more deterministic coding answers
            )
        except Exception as e:
            print(f"Error initializing LLM {self.model_name} at {self.base_url}: {str(e)}")
            return None

    def get_llm(self):
        """Returns the configured LLM instance"""
        return self.llm
        
    def check_connection(self):
        """Checks if the LLM backend is accessible"""
        if not self.llm:
            return False
            
        try:
            # Simple test prompt
            response = self.llm.invoke("Are you there? Reply with YES.")
            return "YES" in response.upper()
        except Exception as e:
            print(f"LLM Connection failed: {str(e)}")
            return False

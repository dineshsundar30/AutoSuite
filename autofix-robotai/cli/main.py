import click
import os
import sys

# Setup logging/formatting
def print_header(title):
    click.secho(f"\n{'='*50}", fg="cyan")
    click.secho(f"🤖 AutoFix-RobotAI: {title}", fg="cyan", bold=True)
    click.secho(f"{'='*50}\n", fg="cyan")

@click.group()
def cli():
    """AutoFix-RobotAI: AI-powered assistant to fix Robot Framework tests."""
    pass

@cli.command()
@click.option('--path', default='.', help='Path to the Robot Framework repository')
def repo_index(path):
    """Scan and index the repository into ChromaDB."""
    print_header("Repository Indexing")
    from repo_indexer.repo_scanner import RepoIndexer
    
    try:
        indexer = RepoIndexer(repo_path=path)
        indexer.index_repository()
        click.secho("\n✅ Indexing complete!", fg="green")
    except Exception as e:
        click.secho(f"\n❌ Error: {str(e)}", fg="red")

@cli.command()
@click.option('--output', required=True, help='Path to the Robot Framework output.xml file')
@click.option('--test-name', default=None, help='Specific test name to analyze (optional)')
def analyze(output, test_name):
    """Analyze a failed test from output.xml without fixing it."""
    print_header("Log Analysis")
    from parsers.robot_log_parser import parse_robot_output
    from llm.llm_manager import LLMManager
    from agents.log_agent import create_log_analysis_agent
    from crewai import Task, Crew
    
    click.secho(f"Parsing {output}...", fg="yellow")
    failures = parse_robot_output(output, target_test_name=test_name)
    
    if not failures:
        click.secho("🎉 No failures found in the log!", fg="green")
        return
        
    llm_manager = LLMManager()
    if not llm_manager.check_connection():
        click.secho("❌ Could not connect to the local LLM! Ensure Ollama is running.", fg="red")
        return
        
    llm = llm_manager.get_llm()
    log_agent = create_log_analysis_agent(llm)
    
    for fail in failures:
        click.secho(f"\nAnalyzing Failure for Test: {fail['test_name']}", fg="magenta", bold=True)
        click.echo(f"  Failing Keyword: {fail['failing_keyword']}")
        click.echo(f"  Message: {fail['message']}\n")
        
        task = Task(
            description=(
                f"Analyze the following Robot Framework failure:\n"
                f"Test Name: {fail.get('test_name')}\n"
                f"Failing Keyword: {fail.get('failing_keyword')}\n"
                f"Message: {fail.get('message')}\n\n"
                f"Determine the exact root cause of this failure."
            ),
            expected_output="A brief paragraph detailing the root cause of the test failure.",
            agent=log_agent
        )
        
        crew = Crew(agents=[log_agent], tasks=[task], verbose=False)
        result = crew.kickoff()
        
        click.secho("\n🧠 AI Analysis:", fg="blue", bold=True)
        click.echo(result)

@cli.command()
@click.option('--log', required=True, help='Path to the Robot Framework output.xml file')
@click.option('--test-name', default=None, help='Specific test case name to fix')
@click.option('--repo-path', default='.', help='Path to the Robot Framework repository')
def fix(log, test_name, repo_path):
    """Analyze a failure and automatically generate a fix patch."""
    print_header("Auto-Fix Generator")
    from parsers.robot_log_parser import parse_robot_output
    from llm.llm_manager import LLMManager
    from repo_indexer.repo_scanner import RepoIndexer
    from agents.crew import AutoFixCrew
    
    click.secho(f"1. Parsing log: {log}", fg="yellow")
    failures = parse_robot_output(log, target_test_name=test_name)
    
    if not failures:
        click.secho("🎉 No failures found to fix!", fg="green")
        return
        
    fail = failures[0] # We fix one at a time for CLI simplicity
    click.secho(f"   Identified target: {fail['test_name']} (Keyword: {fail['failing_keyword']})", fg="green")
    
    click.secho(f"\n2. Gathering Repository Context...", fg="yellow")
    indexer = RepoIndexer(repo_path=repo_path)
    # Search for the failing keyword and test name to give the agents context
    search_query = f"{fail['test_name']} {fail['failing_keyword']}"
    context_docs = indexer.search_similar(search_query, n_results=5)
    
    context_str = ""
    for doc in context_docs:
        context_str += f"\n--- File: {doc['file']} ---\n{doc['content']}\n"
        
    if not context_str.strip():
        click.secho("⚠️ No context found in vector DB. Ensure you have run 'repo-index' first.", fg="yellow")

    click.secho("\n3. Launching AI Crew...", fg="yellow")
    llm_manager = LLMManager()
    if not llm_manager.check_connection():
        click.secho("❌ Could not connect to the local LLM! Ensure Ollama is running.", fg="red")
        return
        
    llm = llm_manager.get_llm()
    fix_crew = AutoFixCrew(llm)
    
    click.echo("   Agents are analyzing root cause, validating locators, and generating a patch...\n")
    
    result = fix_crew.analyze_and_fix(fail, context_str)
    
    click.secho("\n" + "="*50, fg="cyan")
    click.secho("✨ Generated Fix Payload ✨", fg="green", bold=True)
    click.echo(result)
    click.secho("="*50, fg="cyan")
    click.secho("You can apply this patch using `git apply` or review it manually.", fg="magenta")

if __name__ == '__main__':
    cli()

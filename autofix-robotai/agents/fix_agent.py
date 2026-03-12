from crewai import Agent

def create_fix_pr_agent(llm):
    return Agent(
        role='Senior Automation Developer',
        goal='Apply exact code fixes to the repository, create unified diffs (Git patches), and prepare fixes for deployment.',
        backstory='You are a full-stack Automation Developer capable of taking a root cause and a suggested locator '
                  'and turning it into a valid Git patch. You understand Python and Robot Syntax perfectly '
                  'and know how to format your outputs as valid unified diffs.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

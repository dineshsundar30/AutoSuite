from crewai import Agent

def create_repo_understanding_agent(llm):
    return Agent(
        role='Repository Knowledge Engineer',
        goal='Understand the structure, keywords, and locators of the target automation repository.',
        backstory='You are a Repository Maintainer who knows every file, keyword, and locator in the project. '
                  'You help provide the context necessary to fix broken tests by finding the exact file '
                  'where a suspect keyword or locator is defined.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

from crewai import Agent

def create_log_analysis_agent(llm):
    return Agent(
        role='Senior QA Automation Analyst',
        goal='Analyze Robot Framework logs and identify the exact root cause of test failures.',
        backstory='You are an expert QA Engineer with years of experience in Appium and Robot Framework. '
                  'You possess a deep understanding of output.xml files and stack traces, and quickly pinpoint '
                  'whether a failure is due to a missing locator, a timeout, or a logic error.',
        verbose=True,
        allow_delegation=False,
        llm=llm
    )

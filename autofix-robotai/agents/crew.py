from crewai import Task, Crew, Process
from agents.log_agent import create_log_analysis_agent
from agents.repo_agent import create_repo_understanding_agent
from agents.locator_agent import create_locator_fix_agent
from agents.fix_agent import create_fix_pr_agent

class AutoFixCrew:
    def __init__(self, llm):
        self.llm = llm
        
        # Initialize Agents
        self.log_agent = create_log_analysis_agent(llm)
        self.repo_agent = create_repo_understanding_agent(llm)
        self.locator_agent = create_locator_fix_agent(llm)
        self.fix_agent = create_fix_pr_agent(llm)

    def analyze_and_fix(self, failure_info, repo_context):
        """
        Runs the crew to analyze a failure and generate a patch.
        """
        
        # 1. Analyze Log Task
        analyze_task = Task(
            description=(
                f"Analyze the following Robot Framework failure:\n"
                f"Test Name: {failure_info.get('test_name')}\n"
                f"Failing Keyword: {failure_info.get('failing_keyword')}\n"
                f"Message: {failure_info.get('message')}\n\n"
                f"Determine the exact root cause of this failure."
            ),
            expected_output="A brief paragraph detailing the root cause of the test failure.",
            agent=self.log_agent
        )

        # 2. Understand Repo Task (using injected context from our ChromaDB search)
        context_task = Task(
            description=(
                f"Review the provided repository context related to this failure.\n"
                f"Context: {repo_context}\n\n"
                f"Identify what file and what line is likely causing the failure described by the analyst."
            ),
            expected_output="The file path and specific component (keyword/locator) that needs to be fixed.",
            agent=self.repo_agent
        )

        # 3. Fix Validation Task
        fix_strategy_task = Task(
            description=(
                "Based on the root cause and the file identified, determine the correct strategy to fix the issue. "
                "If it's a locator issue, suggest a new Appium locator strategy (e.g., switch from xpath to accessibility id)."
            ),
            expected_output="A clear explanation of how the code should be modified.",
            agent=self.locator_agent
        )

        # 4. Generate Patch Task
        generate_patch_task = Task(
            description=(
                "Create a valid Git patch (unified diff format) that applies the suggested strategy to the target file. "
                "Ensure the result is strictly the diff code block that a developer can apply directly."
            ),
            expected_output="A Git diff patch snippet that fixes the bug.",
            agent=self.fix_agent
        )

        # Orchestrate the workflow
        crew = Crew(
            agents=[self.log_agent, self.repo_agent, self.locator_agent, self.fix_agent],
            tasks=[analyze_task, context_task, fix_strategy_task, generate_patch_task],
            process=Process.sequential,
            verbose=True
        )

        # Execute
        result = crew.kickoff()
        return result

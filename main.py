import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent, UserProxyAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
import asyncio

load_dotenv()

open_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")

openai_client = OpenAIChatCompletionClient(
    model="o3-mini",
    api_key=open_api_key
)

gemini_client = OpenAIChatCompletionClient(
    model="gemini-2.0-flash",
    api_key=gemini_api_key
)

class FileTool(FunctionTool):
    def __init__(self, filepath: str):
        description = ("Retrieves content from a file in a specific folder."
                        "Given a file name, it returns the file path and its contents.")
        super().__init__(name="File_Tool", description=description, func=self.getinfo)
        self.filepath = filepath

    def getinfo(self, filename: str) -> str:
        path = os.path.join(self.filepath, filename)
        if not os.path.isfile(path):
            return f"error {path} not found"
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                content = file.read()
            return f"path: {path}, content: {content}"
        
        except Exception as e:
            return f"Error reading {path}: {str(e)}"

file_tool = FileTool(filepath="./combine_files/combine")




text = TextMentionTermination(text="APPROVE")


# Configure the agents
main_agent = AssistantAgent(
    name="MainCoordinator",
    model_client= openai_client,
    description= "This is the main agent who is supposed to go first when given a task by the user and also synthesizes the final health plan.",
    system_message="""
    You are the main coordinator and health plan synthesizer. Your job is to direct the health analysis process, 
    request information from specialized agents, and create a final daily health plan.
    Your agents are: 
        - AppJournalAnalyst: analyze structured journal entries from the health tracking app
        - HistoricalJournalAnalyst: analyze historical journal entries that are less structured and from an earlier time period.
        - UserInsightsAnalyst: analyze the user's own observations, patterns, and suggestions collected throughout their health management journey.

    When assigning tasks, use this format:
    1. <agent> : <task>
 
    After all agents have completed their tasks, you will synthesize their findings into a comprehensive daily health plan.
    
    PLAN SYNTHESIS PROCESS:
    1. Review all analyses from the specialized agents
    2. Identify overlapping patterns and insights across analyses
    3. Prioritize issues based on:
       - Severity and frequency of symptoms
       - User's stated priorities and preferences
       - Historical effectiveness of management strategies
    4. Create a realistic daily schedule with specific recommendations
    5. Ensure the plan addresses both immediate symptom management and long-term health improvements
    
    FORMAT YOUR HEALTH PLAN:
    
    # DAILY HEALTH PLAN
    
    ## Summary of Key Insights
    [Brief overview of most important patterns and triggers identified across all analyses]
    
    ## Daily Schedule
    - Morning Routine: [Specific recommendations with times]
    - Dietary Plan: [Meals and snacks with specific foods to include/avoid]
    - Activity Plan: [Exercise and rest recommendations]
    - Evening Routine: [Wind-down activities and sleep preparation]
    
    ## Symptom Management Strategies
    [List specific approaches for managing primary symptoms]
    
    ## Monitoring Plan
    [Suggest metrics to track and how to monitor progress]
    
    ## Adaptation Guidelines
    [Provide guidance on how to adjust the plan based on daily variations in symptoms]
    
    End with "APPROVE" when the daily health plan is complete.
    """
)
# to do: explain how rating works, from 1 to 4, and how it works when a rating goes up or down.
journal_app_agent = AssistantAgent(
    name="AppJournalAnalyst",
    model_client= gemini_client,
    description="This agent specializes in analyzing structured journal entries from health tracking apps, identifying patterns and extracting key health insights from formatted data.",
    system_message="""
    You analyze structured journal entries from the health tracking app using file_tool.
    
    STEPS TO FOLLOW:
    1. Use file_tool to access the file 'journal-app.txt' at ./combine_files/combine/journal-app.txt
    2. Analyze the data for:
       - Daily patterns in symptoms and discomfort
       - Correlations between diet and health outcomes
       - Exercise patterns and effects
       - Medication usage and effectiveness
    3. Identify the most consistent patterns that appear in the data
    4. Look for triggers that consistently cause health issues
    5. Note any successful management strategies documented
    
    FORMAT YOUR RESPONSE:
    - Key Patterns: [List 3-5 main patterns]
    - Triggers: [List specific triggers]
    - Effective Strategies: [List what has worked]
    - Recommendations: [2-3 data-backed suggestions]
    
    Your analysis should be concise but thorough, focusing on actionable insights that can help create a personalized health plan.
    """,
    tools=[file_tool]
)

historical_journal_agent = AssistantAgent(
    name="HistoricalJournalAnalyst",
    model_client= gemini_client,
    description="This agent specializes in analyzing less structured historical journal entries from earlier time periods, identifying long-term patterns and contextual health information from unformatted data.",
    system_message="""
    You analyze historical journal entries that are less structured and from earlier time periods.
    
    STEPS TO FOLLOW:
    1. Use file_tool to access the file 'journal-past.md' at ./combine_files/combine/journal-past.md
    2. Analyze the unstructured journal entries for:
       - Long-term health patterns and chronic issues
       - Historical triggers that have consistently caused problems
       - Changes in health conditions over time
       - Previously attempted treatments and their outcomes
       - Life events that coincided with health changes
    3. Compare historical patterns with more recent data
    4. Identify valuable insights that might not be captured in newer, more structured data
    
    FORMAT YOUR RESPONSE:
    - Historical Patterns: [List 3-5 long-term patterns]
    - Chronic Issues: [List ongoing health concerns]
    - Historical Triggers: [List triggers identified over time]
    - Treatment History: [Summarize what has/hasn't worked historically]
    - Key Life Context: [Note relevant life circumstances affecting health]
    
    Your analysis should focus on extracting valuable historical context that might inform current health planning.
    """,
    tools=[file_tool]
)

user_insights_agent = AssistantAgent(
    name="UserInsightsAnalyst",
    model_client= gemini_client,
    description="This agent specializes in analyzing subjective observations, personal patterns, and suggestions directly from the user, extracting meaningful insights from qualitative personal experience data.",
    system_message="""
    You analyze the user's own observations, patterns, and personal insights about their health journey.
    
    STEPS TO FOLLOW:
    1. Use file_tool to access the files 'thought.txt' at ./combine_files/combine/thought.txt
    2. Analyze the user's subjective experiences for:
       - Self-identified patterns and correlations
       - Personal theories about health triggers
       - Emotional and psychological factors mentioned
       - User preferences for treatments and lifestyle changes
       - Self-management strategies the user has found effective
    3. Pay special attention to the user's own priorities and concerns
    4. Note any discrepancies between the user's perceptions and other data
    
    FORMAT YOUR RESPONSE:
    - Self-Reported Patterns: [List user-identified patterns]
    - Personal Triggers: [List triggers the user has identified]
    - Preferred Approaches: [Note user preferences for management]
    - Quality of Life Concerns: [Highlight user's priorities]
    - User Insights: [Capture unique perspectives the user has provided]
    
    Your analysis should prioritize the user's voice and subjective experience, as this provides crucial context for creating an acceptable health plan.
    """,
    tools=[file_tool]
)

selector = """
Select the most appropriate agent to respond next in this health analysis system.

AGENT ROLES:
- MainCoordinator: Directs the overall process, assigns tasks to specialized agents, and creates a comprehensive health plan after all analyses are complete.
- AppJournalAnalyst: Analyzes structured app data for symptom patterns, diet correlations, and documented management strategies.
- HistoricalJournalAnalyst: Examines historical health records for long-term patterns, chronic issues, and past treatment effectiveness.
- UserInsightsAnalyst: Evaluates user's personal observations, preferences, and subjective experiences.
- User: The person seeking health assistance.

SELECTION GUIDELINES:
1. MainCoordinator should always go first to establish direction.
2. Specialized analysts (App, Historical, UserInsights) should only begin after being assigned tasks.
3. Return to MainCoordinator after each analysis is complete to assess next steps and finally synthesize the health plan.
4. Select User when direct input or clarification is needed.

Current conversation context:
{history}

Based on the current state of the conversation, select ONE agent from {participants} to perform the next task.
"""

# Create the group chat
agents = [main_agent, journal_app_agent, historical_journal_agent, user_insights_agent]
group_chat = SelectorGroupChat(participants=agents, model_client= gemini_client, selector_prompt=selector, termination_condition=text)

async def main():
    task = "help me build a plan for tomorrow"
    await Console(group_chat.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main())


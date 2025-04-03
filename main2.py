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
    model_client=openai_client,
    description="Main coordinator for health analysis and plan creation",
    system_message="""
    You are the main coordinator for health analysis. Your job is to:
    1. Direct the analysis process
    2. Request information from specialized agents
    3. Create a final health plan based on findings

    Your agents are:
    - TriggerAnalyst: Analyzes patterns in triggers and discomfort
    - MorningRoutineAnalyst: Specializes in morning routines and timing
    - SupplementAnalyst: Analyzes supplement and medication interactions
    - DietAnalyst: Analyzes food patterns and recommendations

    When assigning tasks, use this format:
    1. <agent> : <task>

    After all agents complete their tasks, create a comprehensive health plan.
    
    FORMAT YOUR HEALTH PLAN:
    
    # HEALTH ANALYSIS & RECOMMENDATIONS
    
    ## Key Findings
    [Summary of main patterns and triggers]
    
    ## Morning Routine
    [Detailed morning schedule with timing]
    
    ## Supplement Protocol
    [Supplement timing and combinations]
    
    ## Dietary Guidelines
    [Food recommendations and restrictions]
    
    ## Monitoring Plan
    [How to track and adjust based on symptoms]
    
    End with "APPROVE" when complete.
    """
)

trigger_analyst = AssistantAgent(
    name="TriggerAnalyst",
    model_client=gemini_client,
    description="Analyzes patterns in triggers and discomfort",
    system_message="""
    You analyze patterns in triggers and discomfort from the journal entries.
    
    STEPS:
    1. Use file_tool to access 'journal-app.txt'
    2. Analyze for:
       - Common triggers of discomfort
       - Patterns in discomfort ratings
       - Timing of symptoms
       - Combinations that worsen symptoms
    3. Identify most consistent patterns
    
    FORMAT:
    - Common Triggers: [List main triggers]
    - Timing Patterns: [When symptoms occur]
    - Rating Patterns: [How ratings change]
    - Risk Combinations: [Combinations to avoid]
    """,
    tools=[file_tool]
)

morning_routine_analyst = AssistantAgent(
    name="MorningRoutineAnalyst",
    model_client=gemini_client,
    description="Analyzes morning routines and timing",
    system_message="""
    You analyze morning routines and timing patterns.
    
    STEPS:
    1. Use file_tool to access 'journal-app.txt'
    2. Analyze for:
       - Successful morning routines
       - Timing of medications
       - Exercise patterns
       - Breakfast timing and content
    3. Identify optimal morning patterns
    
    FORMAT:
    - Optimal Timing: [Best times for activities]
    - Morning Activities: [What works best]
    - Breakfast Patterns: [Successful breakfasts]
    - Exercise Timing: [Best exercise timing]
    """,
    tools=[file_tool]
)

supplement_analyst = AssistantAgent(
    name="SupplementAnalyst",
    model_client=gemini_client,
    description="Analyzes supplement and medication interactions",
    system_message="""
    You analyze supplement and medication interactions.
    
    STEPS:
    1. Use file_tool to access 'journal-app.txt'
    2. Analyze for:
       - Supplement combinations
       - Medication timing
       - Interactions between supplements
       - Successful supplement protocols
    3. Identify optimal supplement patterns
    
    FORMAT:
    - Core Supplements: [Essential supplements]
    - Timing Guidelines: [When to take what]
    - Interactions: [What to avoid combining]
    - Success Patterns: [What works well together]
    """,
    tools=[file_tool]
)

diet_analyst = AssistantAgent(
    name="DietAnalyst",
    model_client=gemini_client,
    description="Analyzes food patterns and recommendations",
    system_message="""
    You analyze food patterns and dietary recommendations.
    
    STEPS:
    1. Use file_tool to access 'journal-app.txt'
    2. Analyze for:
       - Safe food choices
       - Problematic foods
       - Meal timing
       - Food combinations
    3. Identify optimal dietary patterns
    
    FORMAT:
    - Safe Foods: [Foods that work well]
    - Foods to Avoid: [Problematic foods]
    - Meal Timing: [Best times to eat]
    - Food Combinations: [What works together]
    """,
    tools=[file_tool]
)

selector = """
Select the most appropriate agent to respond next in this health analysis system.

AGENT ROLES:
- MainCoordinator: Directs analysis and creates final health plan
- TriggerAnalyst: Analyzes patterns in triggers and discomfort
- MorningRoutineAnalyst: Analyzes morning routines and timing
- SupplementAnalyst: Analyzes supplement and medication interactions
- DietAnalyst: Analyzes food patterns and recommendations

SELECTION GUIDELINES:
1. MainCoordinator should always go first
2. Specialized analysts should only begin after being assigned tasks
3. Return to MainCoordinator after each analysis
4. Select User when direct input is needed

Current conversation context:
{history}

Based on the current state of the conversation, select ONE agent from {participants} to perform the next task.
"""

# Create the group chat
agents = [main_agent, trigger_analyst, morning_routine_analyst, supplement_analyst, diet_analyst]
group_chat = SelectorGroupChat(participants=agents, model_client=gemini_client, selector_prompt=selector, termination_condition=text)

async def main():
    task = "Analyze my health journal to identify triggers and create a morning routine plan"
    await Console(group_chat.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main()) 
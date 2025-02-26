import os
from dotenv import load_dotenv
from autogen_agentchat.agents import AssistantAgent
from autogen_agentchat.conditions import TextMentionTermination
from autogen_agentchat.teams import SelectorGroupChat
from autogen_agentchat.ui import Console
from autogen_ext.models.openai import OpenAIChatCompletionClient
from autogen_core.tools import FunctionTool
import asyncio

load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")

client = OpenAIChatCompletionClient(
    model="o3-mini",
    api_key=api_key
)

text = TextMentionTermination(text="APPROVE")

class FileTool(FunctionTool):
    def __init__(self, folder_path: str):
        description = (
            "Retrieves content from a file in a specific folder. "
            "Given a file name, it returns the file path and its contents."
        )
        super().__init__(name="FileTool", description=description, func=self.get_info)
        self.folder_path = folder_path
    
    def get_info(self, file_name : str) -> str:
        file_path = os.path.join(self.folder_path, file_name)
        if not os.path.isfile(file_path):
            return f"Error: {file_name} not found"
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
            return f"name: {file_name}\n path: {file_path}\n content: {content}"
        except Exception as e:
            return f" Error reading {file_name}: {str(e)}"
        
   
file_tool = FileTool(folder_path="./files")


planner = AssistantAgent(
    name="planner",
    model_client=client,
    description="An agent for planning tasks, this agent should be the first to engage when given a new task.",
    system_message="""
    You are a planning agent.
    Your job is to break down complex tasks into smaller, manageable subtasks.
    Your team members are:
        FileSourcer: provide relevant information 
        

    You only plan and delegate tasks - you do not execute them yourself.

    When assigning tasks, use this format:
    1. <agent> : <task>

    Only when after the agents has complete their task, provide the finding from the agent and end with "APPROVE"."""
)




file_agent = AssistantAgent(
    name="FileSourcer",
    model_client=client,
    description="An agent who has available information for the given files.",
    tools=[file_tool],
    system_message="""You are the FileSourcer agent.
    Your role is to access and provide relevant files to the planner agent using file_tool.
    the file path is ./files/text.txt
    Ensure you have the necessary permissions to access the required files.
    When providing files, use this format:
    File Name: <file_name>
    File Location: <file_location>

    The planner agent will use this information to plan tasks effectively.
    """
) 


selector = """
Select an agent to perform task.

{roles}

Current conversation context:
{history}

Read the above conversation, then select an agent from {participants} to perform the next task.
Make sure the planner agent has assigned tasks before other agents start working.
Only select one agent."""

team = SelectorGroupChat(
    participants=[planner,file_agent],
    model_client=client,
    termination_condition=text,
    selector_prompt=selector
)

task = "what does the text file says."

async def main():
    await Console(team.run_stream(task=task))

if __name__ == "__main__":
    asyncio.run(main())
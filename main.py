import os
import json
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
        super().__init__(name="File Tool", description=description, func=self.getinfo)
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
    system_message="You are the main coordinator. Your job is to direct the health analysis process, request information from specialized agents, and create a final daily health plan.",
    llm_config={"client": openai_client}
)

journal_app_agent = AssistantAgent(
    name="AppJournalAnalyst",
    system_message="You analyze structured journal entries from the health tracking app. You have permission to read the app_journal_data directory. Use your tools to list and read files in this directory.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "app_journal_data", "use_docker": False},
    llm_config={"client": gemini_client},
    tools=app_journal_tools
)

historical_journal_agent = AssistantAgent(
    name="HistoricalJournalAnalyst",
    system_message="You analyze historical journal entries that are less structured and from an earlier time period. You have permission to read the historical_journal_data directory. Use your tools to list and read files in this directory.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "historical_journal_data", "use_docker": False},
    llm_config={"client": gemini_client},
    tools=historical_journal_tools
)

user_insights_agent = AssistantAgent(
    name="UserInsightsAnalyst",
    system_message="You analyze the user's own observations, patterns, and suggestions collected throughout their health management journey. You have permission to read the user_insights directory. Use your tools to list and read files in this directory.",
    human_input_mode="NEVER",
    code_execution_config={"work_dir": "user_insights", "use_docker": False},
    llm_config={"client": gemini_client},
    tools=user_insights_tools
)

plan_synthesizer = AssistantAgent(
    name="HealthPlanSynthesizer",
    system_message="You create a comprehensive daily health plan based on the analyses from all specialized agents. Focus on minimizing abdominal discomfort while creating a realistic schedule.",
    llm_config={"client": gemini_client}
)

# The actual human user
human_user = UserProxyAgent(
    name="User",
    system_message="The end user seeking a personalized daily health plan.",
    human_input_mode="ALWAYS",
    code_execution_config=None
)

# Create the group chat
agents = [main_agent, journal_app_agent, historical_journal_agent, user_insights_agent, plan_synthesizer, human_user]
group_chat = SelectorGroupChat(agents=agents, messages=[], max_round=50)



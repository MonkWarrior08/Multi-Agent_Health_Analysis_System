import os
from dotenv import load_dotenv
from autogen import ConversableAgent

load_dotenv()

api_key = os.environ["OPENAI_API_KEY"]

user = ConversableAgent(
    "user",
    llm_config= False,
    human_input_mode= "ALWAYS",
)

system_message = "You are a medical expert."

agent = ConversableAgent(
    "agent",
    system_message= system_message,
    llm_config= {"config_list": [{"model": "gpt-4o", "api_key": api_key}]},
    human_input_mode= "NEVER",
)

start = user.initiate_chat(agent, message= input())
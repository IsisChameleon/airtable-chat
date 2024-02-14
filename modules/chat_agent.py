from llama_index.agent import OpenAIAgent, ReActAgent
from llama_index.chat_engine.types import AgentChatResponse
from llama_index.llms import OpenAI
from llama_index.memory import BaseMemory, ChatMemoryBuffer
from llama_index.tools import BaseTool
from typing import Any, Dict, Optional, Type, List
from dotenv import load_dotenv
from modules.prompts import system_prompt_llamaindex_ndis_invoicing_agent

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
load_dotenv(override=True)


class ChatAgent:
    def __init__(self, tools:List[BaseTool], model_name: str='gpt-3.5-turbo-0613', temperature: float=0.5):

        llm = OpenAI(model=model_name, temperature=temperature)
        self.memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=[])

        self.agent = OpenAIAgent.from_tools(tools, llm=llm, memory=self.memory, verbose=True, system_prompt=system_prompt_llamaindex_ndis_invoicing_agent)

        logging.log(logging.INFO, f'ChatAgent initialized with {model_name}, temperature {temperature} and tools {tools}')

    def chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        response: AgentChatResponse= self.agent.chat(query)
        return response.response, response.source_nodes
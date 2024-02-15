from llama_index.agent.openai import OpenAIAgent
from llama_index.core.chat_engine.types import AgentChatResponse
from llama_index.llms.openai import OpenAI
# from llama_index.memory import BaseMemory, ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata, BaseTool
from typing import Any, Dict, Optional, Type, List
from dotenv import load_dotenv

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
load_dotenv(override=True)


class ChatAgent:
    def __init__(self, tools:List[BaseTool]):

        llm = OpenAI(model='gpt-4', temperature=0)
        # self.memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=[])

        self.agent = OpenAIAgent.from_tools(tools, verbose=True) # TODO: add system_prompt=system_prompt_llamaindex_ndis_invoicing_agent)

        logging.log(logging.INFO, f'ChatAgent initialized with gpt-4')

    def chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        response: AgentChatResponse= self.agent.chat(query)
        return response.response, response.source_nodes
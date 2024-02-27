from llama_index.agent.openai import OpenAIAgent
from llama_index.core.chat_engine.types import AgentChatResponse
from llama_index.core.agent import ReActAgent
from llama_index.llms.openai import OpenAI
# from llama_index.memory import BaseMemory, ChatMemoryBuffer
from llama_index.core.tools import QueryEngineTool, ToolMetadata, BaseTool
from typing import Any, Dict, Optional, Type, List
from dotenv import load_dotenv
from llama_index.core.query_engine import RouterQueryEngine
from llama_index.core.selectors import LLMSingleSelector

import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.WARN)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))
load_dotenv(override=True)


class ChatAgent:
    def __init__(self, tools:List[BaseTool]):

        llm = OpenAI(model='gpt-4', temperature=0)
        # self.memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=[])

        self.agent = OpenAIAgent.from_tools(tools, llm=llm, verbose=True) # TODO: add system_prompt=system_prompt_llamaindex_ndis_invoicing_agent)

        logging.log(logging.INFO, f'ChatAgent initialized with gpt-4')

    def chat(self, query):
        """
        Start a conversational chat
        """
        response: AgentChatResponse= self.agent.chat(query)
        return response.response, response.source_nodes
    
class ChatAgentReact:
    def __init__(self, tools:List[BaseTool]):

        llm = OpenAI(model='gpt-4', temperature=0)
        # self.memory = ChatMemoryBuffer.from_defaults(llm=llm, chat_history=[])
        context = """
        You are answering questions about the Build Club Members (most ambitious AI builders, tinkerers and founders in Australia and New Zealand) and their build updates
        You will have access to 2 tools, in most cases, start with the semantic_query engine unless it match precisely the db_query_engine tool specifications.

        If the db_query_engine does not return any results, don't jump to conclusion, try the semantic_query_engine tool.
        """

        self.agent = ReActAgent.from_tools(tools, llm=llm, context=context, verbose=True) # TODO: add system_prompt=system_prompt_llamaindex_ndis_invoicing_agent)

        logging.log(logging.INFO, f'React ChatAgent initialized with gpt-4')

    def chat(self, query):
        """
        Start a conversational chat
        """
        response: AgentChatResponse= self.agent.chat(query)

        return response.response, response.source_nodes
    
class ChatAgentRouterQueryEngine:
    def __init__(self, tools:List[BaseTool]):

        llm = OpenAI(model='gpt-4', temperature=0)

        query_engine = RouterQueryEngine(
            selector=LLMSingleSelector.from_defaults(llm=llm),
            query_engine_tools=(tools),
        )

        self.agent = query_engine

        logging.log(logging.INFO, f'ChatAgentRouterQueryEngine initialized with gpt-4')

    def chat(self, query):
        """
        Start a conversational chat with a model via Langchain
        """
        response = self.agent.query(query)
        return response.response, response.source_nodes
    
# class ChatAgentCustomRouterQueryEngine:
#     def __init__(self, tools:List[BaseTool]):

#         llm = OpenAI(model='gpt-4', temperature=0)

#         query_engine = RouterQueryEngine(
#             selector=LLMSingleSelector.from_defaults(llm=llm),
#             query_engine_tools=(tools),
#         )

#         self.agent = query_engine

#         logging.log(logging.INFO, f'ChatAgentRouterQueryEngine initialized with gpt-4')

#     def chat(self, query):
#         """
#         Start a conversational chat with a model via Langchain
#         """
#         response = self.agent.query(query)
#         return response.response, response.source_nodes
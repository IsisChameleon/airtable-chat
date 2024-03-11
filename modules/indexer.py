from llama_index.core import load_index_from_storage, StorageContext
from llama_index.core.indices import VectorStoreIndex, ListIndex
from llama_index.llms.openai import OpenAI
from llama_index.vector_stores.supabase import SupabaseVectorStore
from llama_index.core import SQLDatabase
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core.tools import QueryEngineTool, ToolMetadata, RetrieverTool
from llama_index.core.postprocessor.llm_rerank import LLMRerank
from llama_index.embeddings.openai import OpenAIEmbedding
from llama_index.core import Settings

from modules.reader import CustomAirtableReader
from modules.airtableprompts  import TEXT_TO_SQL_PROMPT

import os
import logging

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

SUPABASE_CONNECTION_STRING=os.getenv('SUPABASE_CONNECTION_STRING')
SQLITE_MEMORY_CONNECTION_STRING="sqlite:///:memory:"
DB_CONNECTION=SUPABASE_CONNECTION_STRING

#https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
from sqlalchemy import (
    create_engine
)

STORAGE_ROOT='.' #local

# https://docs.llamaindex.ai/en/latest/examples/vector_stores/FaissIndexDemo.html

class Indexer:
    def __init__(self, reader: CustomAirtableReader):

        # sqlalchemy
        self.engine = None
        self.default_schema = None
        self._table = None

        self.reader = reader
        self._vector_store_index = None
        self.vectorstoreindex = None
        # self.index_name = index_name
        self._semantic_query_engine = None
        self._db_query_engine = None

        self._sql_database = None
        self._db_query_engine_tool = None
        self._semantic_query_engine_tool = None
        self._db_retriever_tool = None
        self._db_retriever = None
        self._semantic_retriever_tool = None
        self._semantic_retriever = None
        self.listindex = None
        self.vector_store = None
        # global
        Settings.embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimension=1536)

    # def _buildVectorStoreIndex(self):
    #     logging.log(logging.INFO, f'===BUILD VECTOR STORE INDEX=== storing in {STORAGE_ROOT}/storage_vector_store_{self.index_name}')
    #     nodes = self.reader.extract_nodes()
    #     self.vectorstoreindex = VectorStoreIndex(nodes=nodes) #, storage_context=storage_context)

    #     self.vectorstoreindex.storage_context.persist(f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}')
    #     self._semantic_query_engine = None
    #     return self.vectorstoreindex
    
    # def _getVectorStoreIndex(self, reload=False):
    #     persist_dir=f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}'
    #     if os.path.exists(persist_dir) and os.path.isdir(persist_dir) and reload==False:
    #         logging.log(logging.INFO, f'===LOADING VECTOR STORE INDEX=== from storage in {STORAGE_ROOT}/storage_vector_store_{self.index_name}')
    #         storage_context = StorageContext.from_defaults(
    #             persist_dir=persist_dir
    #         )
    #         self.vectorstoreindex = load_index_from_storage(storage_context=storage_context)
    #         self._semantic_query_engine = None
    #         return self.vectorstoreindex
    #     return self._buildVectorStoreIndex()
    
    def _getVectorStoreIndex_supabase(self):
        self.vector_store = SupabaseVectorStore(
            postgres_connection_string=SUPABASE_CONNECTION_STRING, 
            collection_name='members_and_build_updates'
        )
        # TO DO: query vector store to find out if there is anything we need to build 
        # if YES: build vector store index, if NO: return without building
        logging.log(logging.INFO, f'===Get VectorStoreIndex from SUPABASE=== members_and_build_updates using openai text-embedding-3-small dim 1536')
        embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimension=1536, api_key=os.environ['OPENAI_API_KEY'])
        self.vectorstoreindex = VectorStoreIndex.from_vector_store(self.vector_store, use_async=True, embed_model=embed_model)
        return self.vectorstoreindex

    def _buildVectorStoreIndex_supabase(self):
        logging.log(logging.INFO, f'===BUILD VECTOR STORE INDEX insert nodes into supabase === members_and_build_updates')
        nodes = self.reader.extract_nodes()
        self.vector_store = SupabaseVectorStore(
            postgres_connection_string=SUPABASE_CONNECTION_STRING, 
            collection_name='members_and_build_updates'
        )
        embed_model = OpenAIEmbedding(model="text-embedding-3-small", dimension=1536, api_key=os.environ['OPENAI_API_KEY'])
        logging.log(logging.INFO, f'===BUILD VECTOR STORE INDEX using openai text-embedding-3-small dim 1536')
        self.vectorstoreindex = VectorStoreIndex.from_vector_store(self.vector_store, use_async=True, embed_model=embed_model)
        self.vectorstoreindex.insert_nodes(nodes)
        return self.vectorstoreindex

    
    @property
    def semantic_query_engine(self):
        if self.vectorstoreindex is None:
            _ = self._getVectorStoreIndex_supabase()
        # if self._semantic_query_engine is None:
        llm = OpenAI(model="gpt-4", temperature=0)
        print('NODE POSTPROCESSOR LLMRERANK')
        # node_postprocessor_1 = SimilarityPostprocessor(similarity_cutoff=0.75)
        node_postprocessor_2 = LLMRerank(llm=llm)
        self._semantic_query_engine = self.vectorstoreindex.as_query_engine(
            llm=llm, 
            # retriever kwargs
            similarity_top_k=8, 
            # post processing
            node_postprocessors=[node_postprocessor_2])
        return self._semantic_query_engine

    @property
    def semantic_retriever(self):
        if self.vectorstoreindex is None:
            _ = self._getVectorStoreIndex_supabase()
        if self._semantic_retriever is None:
            llm = OpenAI(model="gpt-4", temperature=0)
            self._semantic_retriever = self.vectorstoreindex.as_retriever(llm=llm)
        return self._semantic_query_engine
    
    # to do create vector store retriever as tool 
    # to have function calling /workspaces/ml-learning/.venv/lib/python3.11/site-packages/llama_index/core/indices/vector_store/retrievers/retriever.py
    
    def _getSQLDatabase(self):
        engine = create_engine(DB_CONNECTION, pool_pre_ping=True)

        self._sql_database = SQLDatabase(engine, include_tables=["build_club_members"])
        self._db_query_engine = None
        return self._sql_database
    
    @property
    def db_query_engine(self):
        logging.log(logging.INFO, f'===db_query_engine===')
        if  self._sql_database is None:           
            _ = self._getSQLDatabase()

        if self._db_query_engine is None:

            llm = OpenAI(model="gpt-4", temperature=0)
            self._db_query_engine = NLSQLTableQueryEngine(
                sql_database=self._sql_database,
                llm=llm,
                tables=["build_club_members"],
                context_query_kwargs={
                    "build_club_members": "This table contains the members of the build club"
                },
                text_to_sql_prompt=TEXT_TO_SQL_PROMPT,
                verbose=True
            )
            logging.log(logging.INFO, f'==Db query engine created==')
        logging.log(logging.INFO, f'Returning Db query engine')
        return self._db_query_engine

    @property
    def db_retriever(self):
        logging.log(logging.INFO, f'===db_retriever===')
        if  self._sql_database is None:           
            _ = self._getSQLDatabase()

        if self._db_retriever is None:

            llm = OpenAI(model="gpt-4", temperature=0)
            self._db_retriever = NLSQLRetriever(
                sql_database=self._sql_database,
                llm=llm,
                tables=["build_club_members"],
                text_to_sql_prompt=TEXT_TO_SQL_PROMPT,
                verbose=True
            )
            logging.log(logging.INFO, f'==Db retriever created==')
        logging.log(logging.INFO, f'Returning Db retriever')
        return self._db_retriever
    
    @property
    def tools(self):
        self._semantic_query_engine_tool = QueryEngineTool(
            query_engine=self.semantic_query_engine,
            metadata=ToolMetadata(
                    name="semantic_query_engine",
                    description="""Semantic search: useful for when you want to answer queries about members projects, their startups,
                      what they are building, their build updates, and what are their interests and passions, and in what domain their are working. 
                      This is the default tool. Use it when other tools don't return any useful information to answer the question.""",
                ),
        )
        self._db_query_engine_tool = QueryEngineTool(
                query_engine=self.db_query_engine,
                metadata=ToolMetadata(
                    name="db_query_engine",
                    description="""Retrieve information about members using SQL queries:
                        useful for when you want to answer queries about members skills (engineering, AI/ML researcher, product owner), 
                        if they are accepted in the club, their linked in url, location, their build squad, or name.
                        ALso try it when Semantic search doesn't return anything.""",
                ),
        )
        # self._db_retriever_tool = RetrieverTool(
        #         retriever=self.db_retriever,
        #         metadata=ToolMetadata(
        #             name="db_query_engine",
        #             description="""Retrieve information about members using SQL queries:
        #                 useful for when you want to answer queries about members skills (engineering, AI/ML researcher, domain expert, product owner), 
        #                 if they are accepted in the club, their linked in url, location, their build squad, name, skills.
        #                 Useful when Semantic search doesn't return anything useful."""
        #         )
        # )

        return [self._semantic_query_engine_tool, self._db_query_engine_tool]
    
    # @property
    # def retriever_tools(self):
    #     if self._db_retriever_tool is None:
    #         self._db_retriever_tool = RetrieverTool(
    #             retriever=self.db_retriever,
    #             metadata=ToolMetadata(
    #                 name="db_query_engine",
    #                 description="useful for when you want to answer queries about members career, role, linked in url, name, skills, location, phone number, accepted in club or not, referrer name.",
    #             ),
    #     )
    #     if self._semantic_retriever_tool is None:
    #         self._semantic_retriever_tool = RetrieverTool(
    #             retriever=self.semantic_retriever,
    #             metadata=ToolMetadata(
    #                     name="semantic_query_engine",
    #                     description="useful for when you want to answer queries about members projects and startups (past and present), what they hope from the club and startups, or what they are building",
    #                 ),
    #     )
    #     return [self._db_retriever_tool, self._semantic_retriever_tool]

    





from llama_index.core import ServiceContext, load_index_from_storage, StorageContext
from llama_index.core.indices import VectorStoreIndex, ListIndex
from llama_index.llms.openai import OpenAI

from llama_index.legacy.vector_stores.faiss import FaissVectorStore
from llama_index.legacy.vector_stores import SupabaseVectorStore
from llama_index.core.readers.base import BaseReader
from llama_index.core import SQLDatabase
from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core.tools import QueryEngineTool, ToolMetadata, RetrieverTool
from llama_index.core.postprocessor.llm_rerank import LLMRerank

from modules.reader import CustomAirtableReader
from modules.airtableprompts  import TEXT_TO_SQL_PROMPT

from typing import Any, Dict, Optional, Type, List
import os
from pathlib import Path
import logging
# import faiss

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

SUPABASE_CONNECTION_STRING=os.getenv('SUPABASE_CONNECTION_STRING')
SQLITE_MEMORY_CONNECTION_STRING="sqlite:///:memory:"
DB_CONNECTION=SUPABASE_CONNECTION_STRING

#https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
from sqlalchemy import (
    insert,
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Boolean,
    Integer,
    select,
    column,
)

STORAGE_ROOT='.' #local

# https://docs.llamaindex.ai/en/latest/examples/vector_stores/FaissIndexDemo.html

class Indexer:
    def __init__(self, reader: CustomAirtableReader, index_name: str):

        # sqlalchemy
        self.engine = None
        self.default_schema = None
        self._table = None

        self.reader = reader
        self._vector_store_index = None
        self.vectorstoreindex = None
        self.index_name = index_name
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

    def _buildVectorStoreIndex(self):
        logging.log(logging.INFO, f'===BUILD VECTOR STORE INDEX=== storing in {STORAGE_ROOT}/storage_vector_store_{self.index_name}')
        nodes = self.reader.extract_nodes()
        self.vectorstoreindex = VectorStoreIndex(nodes=nodes) #, storage_context=storage_context)

        self.vectorstoreindex.storage_context.persist(f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}')
        self._semantic_query_engine = None
        return self.vectorstoreindex

    # def loadIndex(self, reload_from_disk=False):
    #     if self.vectorstoreindex is None or reload_from_disk==True:
        
    #         persist_dir=f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}'
    #         # vector_store = FaissVectorStore.from_persist_dir(persist_dir)
    #         storage_context = StorageContext.from_defaults(
    #             persist_dir=persist_dir
    #         )
    #         self.vectorstoreindex = load_index_from_storage(storage_context=storage_context)
    #         self._semantic_query_engine = None
    #     return self.vectorstoreindex
    
    def _getVectorStoreIndex(self, reload=False):
        persist_dir=f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}'
        if os.path.exists(persist_dir) and os.path.isdir(persist_dir) and reload==False:
            logging.log(logging.INFO, f'===LOADING VECTOR STORE INDEX=== from storage in {STORAGE_ROOT}/storage_vector_store_{self.index_name}')
            storage_context = StorageContext.from_defaults(
                persist_dir=persist_dir
            )
            self.vectorstoreindex = load_index_from_storage(storage_context=storage_context)
            self._semantic_query_engine = None
            return self.vectorstoreindex
        return self._buildVectorStoreIndex()
    
    def _buildVectorStoreIndex_supabase(self):
        self.vector_store = SupabaseVectorStore(
            postgres_connection_string=SUPABASE_CONNECTION_STRING, 
            collection_name='build_club_members'
        )
        
        storage_context = StorageContext.from_defaults(vector_store=self.vector_store)
        logging.log(logging.INFO, f'===BUILD VECTOR STORE INDEX FOR SUPABASE===')
        nodes = self.reader.extract_nodes()
        self.vectorstoreindex = VectorStoreIndex.from_vector_store(self.vector_store)
        # self.vectorstoreindex = VectorStoreIndex(nodes=nodes, storage_context=storage_context)
        return self.vectorstoreindex

    
    @property
    def semantic_query_engine(self):
        if self.vectorstoreindex is None:
            _ = self._getVectorStoreIndex(reload=False)
        # if self._semantic_query_engine is None:
        llm = OpenAI(model="gpt-4", temperature=0)
        print('NODE POSTPROCESSOR LLMRERANK')
        node_postprocessor = LLMRerank(llm=llm)
        self._semantic_query_engine = self.vectorstoreindex.as_query_engine(llm=llm, node_postprocessor=node_postprocessor)
        return self._semantic_query_engine

    @property
    def semantic_retriever(self):
        if self.vectorstoreindex is None:
            _ = self._getVectorStoreIndex(reload=False)
        if self._semantic_retriever is None:
            llm = OpenAI(model="gpt-4", temperature=0)
            self._semantic_retriever = self.vectorstoreindex.as_retriever(llm=llm)
        return self._semantic_query_engine
    
    # to do create vector store retriever as tool 
    # to have function calling /workspaces/ml-learning/.venv/lib/python3.11/site-packages/llama_index/core/indices/vector_store/retrievers/retriever.py
    
    def _getSQLDatabase(self):
        # logging.log(logging.INFO, f'===BUILDING NEW=== Initializing sqlite in memory')
        # self.engine = create_engine("sqlite:///:memory:")
        # self.default_schema = MetaData()
        # self._table = self._design_build_club_members_table()
        # self.default_schema.create_all(self.engine)

        # Create an engine
        engine = create_engine(DB_CONNECTION)

        # # Initialize metadata
        # metadata = MetaData()

        # # Reflect the table
        # build_club_members = Table('build_club_members', metadata, autoload_with=engine)

        # rows = self.reader.extract_rows2()

        # for row in rows:
        #     stmt = insert(build_club_members).values(**row)
        #     with self.engine.begin() as connection:
        #         cursor = connection.execute(stmt)
        # logging.log(logging.INFO, f'===YAY=== All rows inserted in build_club_members table')

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
                text_to_sql_prompt=TEXT_TO_SQL_PROMPT,
                verbose=True
            )
            logging.log(logging.INFO, f'==Db query engine created==')
        logging.log(logging.INFO, f'Returning Db query engine')
        return self._db_query_engine


        # sql_database (SQLDatabase): SQL database.
        # text_to_sql_prompt (BasePromptTemplate): Prompt template for text-to-sql.
        #     Defaults to DEFAULT_TEXT_TO_SQL_PROMPT.
        # context_query_kwargs (dict): Mapping from table name to context query.
        #     Defaults to None.
        # tables (Union[List[str], List[Table]]): List of table names or Table objects.
        # table_retriever (ObjectRetriever[SQLTableSchema]): Object retriever for
        #     SQLTableSchema objects. Defaults to None.
        # context_str_prefix (str): Prefix for context string. Defaults to None.
        # service_context (ServiceContext): Service context. Defaults to None.
        # return_raw (bool): Whether to return plain-text dump of SQL results, or parsed into Nodes.
        # handle_sql_errors (bool): Whether to handle SQL errors. Defaults to True.
        # sql_only (bool) : Whether to get only sql and not the sql query result.
        #     Default to False.
        # llm (Optional[LLM]): Language model to use.
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
        print('GETTTING TOOLS ####################################')
        if self._db_query_engine_tool is None:
            self._db_query_engine_tool = QueryEngineTool(
                query_engine=self.db_query_engine,
                metadata=ToolMetadata(
                    name="db_query_engine",
                    description="useful for when you want to answer queries about members career or role (skills), linked in url, name, skills.",
                ),
        )
        # if self._semantic_query_engine_tool is None:
        self._semantic_query_engine_tool = QueryEngineTool(
            query_engine=self.semantic_query_engine,
            metadata=ToolMetadata(
                    name="semantic_query_engine",
                    description="useful for when you want to answer queries about members present and past projects and startups, or what they are building",
                ),
        )
        return [self._db_query_engine_tool, self._semantic_query_engine_tool]
    
    @property
    def retriever_tools(self):
        if self._db_retriever_tool is None:
            self._db_retriever_tool = RetrieverTool(
                retriever=self.db_retriever,
                metadata=ToolMetadata(
                    name="db_query_engine",
                    description="useful for when you want to answer queries about members career, role, linked in url, name, skills, location, phone number, accepted in club or not, referrer name.",
                ),
        )
        if self._semantic_retriever_tool is None:
            self._semantic_retriever_tool = RetrieverTool(
                retriever=self.semantic_retriever,
                metadata=ToolMetadata(
                        name="semantic_query_engine",
                        description="useful for when you want to answer queries about members projects and startups (past and present), what they hope from the club and startups, or what they are building",
                    ),
        )
        return [self._db_retriever_tool, self._semantic_retriever_tool]

    





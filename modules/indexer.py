from llama_index.core import ServiceContext, load_index_from_storage, StorageContext
from llama_index.core.indices import VectorStoreIndex, ListIndex
from llama_index.llms.openai import OpenAI

from llama_index.legacy.vector_stores.faiss import FaissVectorStore
from llama_index.core.readers.base import BaseReader
from llama_index.core import SQLDatabase
from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata, RetrieverTool

from modules.reader import CustomAirtableReader
from modules.airtableprompts  import TEXT_TO_SQL_PROMPT

from typing import Any, Dict, Optional, Type, List
import os
from pathlib import Path
import logging
# import faiss

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

        self.reader = reader
        self._vector_store_index = None
        self.vectorstoreindex = None
        self.index_name = index_name
        self._semantic_query_engine = None
        self._db_query_engine = None
        self.engine = None
        self.default_schema = None
        self._table = None
        self.sql_database = None
        self._db_query_engine_tool = None
        self._semantic_query_engine_tool = None
        self._db_retriever_tool = None
        self._semantic_retriever_tool = None
        self.listindex = None

    def _buildVectorStoreIndex(self):
        logging.log(logging.INFO, f'===BUILD VECTOR STORE INDEX=== storing in {STORAGE_ROOT}/storage_vector_store_{self.index_name}')
        nodes = self.reader.extract_nodes()

        # SETUP VECTOR STORE
        # dimensions of text-ada-embedding-002
        # d = 1536
        # faiss_index = faiss.IndexFlatL2(d)
        # vector_store = FaissVectorStore(faiss_index=faiss_index)
        # storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.vectorstoreindex = VectorStoreIndex(nodes=nodes) #, storage_context=storage_context)
        # self.listindex = ListIndex(nodes=nodes)
        # save index to disk
        self.vectorstoreindex.storage_context.persist(f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}')
        self._semantic_query_engine = None
        return self.vectorstoreindex

    def loadIndex(self, reload_from_disk=False):
        if self.vectorstoreindex is None or reload_from_disk==True:
        
            persist_dir=f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}'
            # vector_store = FaissVectorStore.from_persist_dir(persist_dir)
            storage_context = StorageContext.from_defaults(
                persist_dir=persist_dir
            )
            self.vectorstoreindex = load_index_from_storage(storage_context=storage_context)
            self._semantic_query_engine = None
        return self.vectorstoreindex
    
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

    
    # @property
    # def vector_store_index(self):
    #     # check if storage already exists
    #     persist_dir=f'{STORAGE_ROOT}/storage_vector_store_{self.index_name}'
    #     if not os.path.exists(persist_dir):
    #         self._buildVectorStoreIndex()


    
    @property
    def semantic_query_engine(self):
        if self.vectorstoreindex is None:
            _ = self._getVectorStoreIndex(reload=False)
        if self._semantic_query_engine is None:
            llm = OpenAI(model="gpt-4", temperature=0)
            self._semantic_query_engine = self.vectorstoreindex.as_query_engine(llm=llm)
        return self._semantic_query_engine
    
    # to do create vector store retriever as tool 
    # to have function calling /workspaces/ml-learning/.venv/lib/python3.11/site-packages/llama_index/core/indices/vector_store/retrievers/retriever.py

    def _design_build_club_members_table(self) -> Table:
        logging.log(logging.INFO, f'Design build_club_members table')
        metadata_obj = self.default_schema
        table_name = "build_club_members"
        build_club_members = Table(
            table_name,
            metadata_obj,
            Column("id", String(256), primary_key=True),
            Column("name", String(256)),
            Column("linkedin_url", String(512)),
            Column("skill_1", String(128)),
            Column("skill_2", String(128)),
            Column("skill_3", String(128)),
            Column("skill_4", String(128)),
            Column("based_in_sydney", String(256)),
            Column("member_location", String(256)),
            Column("member_acceptance_in_club", Boolean()),
            Column("ai_builder_linkedin_badge", String(256)),
            Column("referee", String(256)),
            Column("referrer_name", String(256)),
            Column("assignee", String(256)),
            Column("status", String(256)),
            Column("phone_number", String(256)),
            Column("are_you_building_in_squad", String(1024)),
            Column("best_time_for_build_sessions", String(1024)),
            Column("keen_for_ai_meetup", String(128)),
            Column("expectation_from_joining_club", String(4096)),
            Column("build_project", String(4096)),
            Column("past_work", String(4096))
        )
        # metadata_obj.create_all(self.engine)
        return build_club_members
    
    @property
    def db_query_engine(self):
        logging.log(logging.INFO, f'===db_query_engine===')
        if self._db_query_engine is None:
            logging.log(logging.INFO, f'===BUILDING NEW=== Initializing sqlite in memory')
            self.engine = create_engine("sqlite:///:memory:")
            self.default_schema = MetaData()
            self._table = self._design_build_club_members_table()
            self.default_schema.create_all(self.engine)

            rows = self.reader.extract_rows2()

            for row in rows:
                stmt = insert(self._table).values(**row)
                with self.engine.begin() as connection:
                    cursor = connection.execute(stmt)
            logging.log(logging.INFO, f'===YAY=== All rows inserted in build_club_members table')

            self.sql_database = SQLDatabase(self.engine, include_tables=["build_club_members"])
            llm = OpenAI(model="gpt-4", temperature=0)
            self._db_query_engine = NLSQLTableQueryEngine(
                sql_database=self.sql_database,
                llm=llm,
                tables=["build_club_members"],
                text_to_sql_prompt=TEXT_TO_SQL_PROMPT,
                verbose=True
            )
            logging.log(logging.INFO, f'==Db query engine created==')
        logging.log(logging.INFO, f'Returning Db query engine')
        return self._db_query_engine
    
    @property
    def tools(self):
        if self._db_query_engine_tool is None:
            self._db_query_engine_tool = QueryEngineTool(
                query_engine=self.db_query_engine,
                metadata=ToolMetadata(
                    name="db_query_engine",
                    description="useful for when you want to answer queries about members career or role (skills), linked in url, name, skills.",
                ),
        )
        if self._semantic_query_engine_tool is None:
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
                query_engine=self.db_query_engine,
                metadata=ToolMetadata(
                    name="db_query_engine",
                    description="useful for when you want to answer queries about members career, role, linked in url, name, skills, location, phone number, accepted in club or not, referrer name.",
                ),
        )
        if self._semantic_retriever_tool is None:
            self._semantic_retriever_tool = RetrieverTool(
                query_engine=self.semantic_query_engine,
                metadata=ToolMetadata(
                        name="semantic_query_engine",
                        description="useful for when you want to answer queries about members projects and startups (past and present), what they hope from the club and startups, or what they are building",
                    ),
        )
        return [self._db_retriever_tool, self._semantic_retriever_tool]

    





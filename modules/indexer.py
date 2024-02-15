from llama_index.core import ServiceContext, load_index_from_storage, StorageContext
from llama_index.core.indices import VectorStoreIndex
from llama_index.llms.openai import OpenAI

from llama_index.legacy.vector_stores.faiss import FaissVectorStore
from llama_index.core.readers.base import BaseReader
from llama_index.core import SQLDatabase
from llama_index.core.prompts.base import PromptTemplate
from llama_index.core.prompts.prompt_type import PromptType
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.core.tools import QueryEngineTool, ToolMetadata

from modules.reader import CustomAirtableReader
from modules.prompts import TEXT_TO_SQL_PROMPT

from typing import Any, Dict, Optional, Type, List
import os
from pathlib import Path
# import faiss

#https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
from sqlalchemy import (
    insert,
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Integer,
    select,
    column,
)

STORAGE_ROOT='.' #local

# https://docs.llamaindex.ai/en/latest/examples/vector_stores/FaissIndexDemo.html

class Indexer:
    def __init__(self, reader: CustomAirtableReader, index_name: str):

        self.reader = reader
        self.index = None
        self.index_name = index_name
        self._semantic_query_engine = None
        self._db_query_engine = None
        self.engine = None
        self.default_schema = None
        self._table = None
        self.sql_database = None
        self._db_query_engine_tool = None
        self._semantic_query_engine_tool = None

    def buildVectorStoreIndex(self):
        nodes = self.reader.extract_nodes()

        # SETUP VECTOR STORE
        # dimensions of text-ada-embedding-002
        # d = 1536
        # faiss_index = faiss.IndexFlatL2(d)
        # vector_store = FaissVectorStore(faiss_index=faiss_index)
        # storage_context = StorageContext.from_defaults(vector_store=vector_store)
        self.index = VectorStoreIndex(nodes=nodes) #, storage_context=storage_context)
        # save index to disk
        self.index.storage_context.persist(f'{STORAGE_ROOT}/storage_{self.index_name}')
        self._semantic_query_engine = None
        return self.index

    def loadIndex(self, reload_from_disk=False):
        if self.index is None or reload_from_disk==True:
        
            persist_dir=f'{STORAGE_ROOT}/storage_{self.index_name}'
            # vector_store = FaissVectorStore.from_persist_dir(persist_dir)
            storage_context = StorageContext.from_defaults(
                persist_dir=persist_dir
            )
            self.index = load_index_from_storage(storage_context=storage_context)
            self._semantic_query_engine = None
        return self.index
    
    @property
    def semantic_query_engine(self):
        if self.index is None:
            _ = self.buildVectorStoreIndex()
        if self._semantic_query_engine is None:
            llm = OpenAI(model="gpt-4", temperature=0)
            self._semantic_query_engine = self.index.as_query_engine(llm=llm)
        return self._semantic_query_engine
    
    # to do create vector store retriever as tool 
    # to have function calling /workspaces/ml-learning/.venv/lib/python3.11/site-packages/llama_index/core/indices/vector_store/retrievers/retriever.py

    def _design_build_club_members_table(self) -> Table:
        metadata_obj = self.default_schema
        table_name = "build_club_members"
        build_club_members = Table(
            table_name,
            metadata_obj,
            Column("id", String(256), primary_key=True),
            Column("member_name", String(256)),
            Column("linkedin_url", String(512)),
            Column("skill_1", String(128)),
            Column("skill_2", String(128)),
            Column("skill_3", String(128)),
            Column("skill_4", String(128)),
            Column("build_project", String(4096))
        )
        metadata_obj.create_all(self.engine)
        return build_club_members
    
    @property
    def db_query_engine(self):
        if self._db_query_engine is None:
            self.engine = create_engine("sqlite:///:memory:")
            self.default_schema = MetaData()
            self._table = self._design_build_club_members_table()
            self.default_schema.create_all(self.engine)

            rows = self.reader.extract_rows()

            for row in rows:
                stmt = insert(self._table).values(**row)
                with self.engine.begin() as connection:
                    cursor = connection.execute(stmt)

            self.sql_database = SQLDatabase(self.engine, include_tables=["build_club_members"])
            llm = OpenAI(model="gpt-4", temperature=0)
            self._db_query_engine = NLSQLTableQueryEngine(
                sql_database=self.sql_database,
                llm=llm,
                tables=["build_club_members"],
                text_to_sql_prompt=TEXT_TO_SQL_PROMPT,
                verbose=True
            )
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
                        description="useful for when you want to answer queries about members projects and startups, or what they are building",
                    ),
        )
        return [self._db_query_engine_tool, self._semantic_query_engine_tool]





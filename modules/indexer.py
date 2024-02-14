# This class will create an index for all the pdfs (version 1) and an index for the xls table of the price guide
from llama_index import (
    ServiceContext, 
    StorageContext, 
    VectorStoreIndex, 
    load_index_from_storage)
from llama_index.llms import OpenAI
from llama_index.text_splitter import TokenTextSplitter
from llama_index.node_parser import SimpleNodeParser
from llama_index.vector_stores import FaissVectorStore
from llama_index.readers.base import BaseReader

from modules.reader import CustomAirtableReader

from typing import Any, Dict, Optional, Type, List
import os
from pathlib import Path
import faiss

STORAGE_ROOT='.' #local

# https://docs.llamaindex.ai/en/latest/examples/vector_stores/FaissIndexDemo.html

class Indexer:
    def __init__(self, reader: BaseReader | None=None):

        self.reader = reader or CustomAirtableReader()


    def buildVectorStoreIndex(self,  index_name: str, base_id: str, table_id: str, folder: str | None=None):
        documents = self.reader.load_data(folder=folder, base_id=base_id, table_id=table_id)
        # dimensions of text-ada-embedding-002
        d = 1536
        faiss_index = faiss.IndexFlatL2(d)
        vector_store = FaissVectorStore(faiss_index=faiss_index)
        storage_context = StorageContext.from_defaults(vector_store=vector_store)
        index = VectorStoreIndex.from_documents(
                documents, storage_context=storage_context
        )
        # save index to disk
        index.storage_context.persist(f'{STORAGE_ROOT}/storage_{index_name}')
        return index

    def loadIndex(self, index_name: str):
        persist_dir=f'{STORAGE_ROOT}/storage_{index_name}'
        vector_store = FaissVectorStore.from_persist_dir(persist_dir)
        storage_context = StorageContext.from_defaults(
            vector_store=vector_store, persist_dir=persist_dir
        )
        index = load_index_from_storage(storage_context=storage_context)
        return index

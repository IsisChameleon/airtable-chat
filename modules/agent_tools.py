from modules.indexer import Indexer
from llama_index.core import VectorStoreIndex, get_response_synthesizer
from llama_index.retrievers import VectorIndexRetriever
from llama_index.query_engine import RetrieverQueryEngine
from llama_index.postprocessor import SimilarityPostprocessor

AIRTABLE_BC_MEMBERS_INDEX = 'Airtable_BC_Members'

def getAgentTools():

    index = Indexer().loadIndex(AIRTABLE_BC_MEMBERS_INDEX)

    # configure retriever (https://docs.llamaindex.ai/en/stable/understanding/querying/querying.html#configuring-response-synthesis)
    retriever = VectorIndexRetriever(
        index=index,
        similarity_top_k=10,
    )

    # configure response synthesizer
    response_synthesizer = get_response_synthesizer()

    tools = Tools().withQueryEngineTool(provider_index, 'mytool', 'Use to answer queries about NDIS Price Guide, claiming for providers')
    
    return tools.tools
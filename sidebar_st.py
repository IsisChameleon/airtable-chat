import streamlit as st

class Sidebar:

    MODEL_OPTIONS = ["gpt-3.5-turbo-16k", "gpt-4"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def about():
        about = st.sidebar.expander("Find My Db 🤖")
        sections = [
            "#### Vector Database",
            "#### Powered by [Llamaindex](), [OpenAI](https://platform.openai.com/docs/models/gpt-3-5) and [Streamlit](https://github.com/streamlit/streamlit) ⚡",
            "#### Source code: [isisChameleon/airtable-chatbot](https://github.com/IsisChameleon)",
        ]
        for section in sections:
            about.write(section)

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)
        
    @staticmethod
    def on_model_parameters_change_callback():
        st.session_state["tweak"] = True

    # def model_selector(self):
    #     model = st.selectbox(label="Model", 
    #                          options=self.MODEL_OPTIONS, 
    #                          on_change=self.on_model_parameters_change_callback)
    #     st.session_state["model"] = model

    # def temperature_slider(self):
    #     temperature = st.slider(
    #         label="Temperature",
    #         min_value=self.TEMPERATURE_MIN_VALUE,
    #         max_value=self.TEMPERATURE_MAX_VALUE,
    #         value=self.TEMPERATURE_DEFAULT_VALUE,
    #         step=self.TEMPERATURE_STEP,
    #         on_change=self.on_model_parameters_change_callback
    #     )
    #     st.session_state["temperature"] = temperature
        
    def show_options(self):
        if "tweak" not in st.session_state:
            st.session_state.tweak = False
        with st.sidebar.expander("⚙️ Tweak Niddy", expanded=False):

            self.reset_chat_button()
            self.model_selector()
            # self.temperature_slider()
            st.session_state.setdefault("model", self.MODEL_OPTIONS[0])
            st.session_state.setdefault("temperature", self.TEMPERATURE_DEFAULT_VALUE)

    #Contact
    @staticmethod
    def show_contact():
        
        with st.sidebar.expander("📧 Contact"):

            st.write("**GitHub:** [Vector Db Chat](https://github.com/IsisChameleon/vectordb-chat)")
            st.write("**Made for ** [The Builders Club](https://www.thebuilderclub.org/)")
            st.write("**Contributions or suggestions welcome! ** : isisdesade@gmail.com")

    @staticmethod
    # def url_selector():
    #     url_list = [
    #         {"url": "", "description": "Select a URL..."},
    #         {"url": "https://www.deeplake.ai/", "description": "DeepLake"},
    #         {"url": "https://www.datastax.com/products/datastax-astra", "description": "DataStax Astra DB"},
    #         {'url': 'https://learn.microsoft.com/en-us/azure/cosmos-db/mongodb/vcore/', 'description': 'Azure CosmosDB MongoDB vCore'},
    #         {'url': 'https://bageldb.com/', 'description': 'BagelDB'},
    #         {'url': 'https://cassandra.apache.org/doc/latest/cassandra/getting-started/vector-search-quickstart.html', 'description': 'Cassandra'},
    #         {'url': 'https://docs.trychroma.com/', 'description': 'ChromaDB'},
    #         {'url': 'https://learn.microsoft.com/en-us/azure/search/search-what-is-azure-search', 'description': 'Azure AI Search'},
    #         {'url': 'https://cn.aliyun.com/product/ai/dashvector?from_alibabacloud=&spm=a2c4g.2510225.0.0.11f0250eWf0kAy', 'description': 'Dashvector'},
    #         {'url': 'https://www.deeplake.ai/', 'description': 'Deeplake'},
    #         {'url': 'https://www.elastic.co/elasticsearch/vector-database', 'description': 'Elasticsearch'},
    #         {'url': 'https://epsilla.com/', 'description': 'Epsilla'},
    #         {'url': 'https://faiss.ai/', 'description': 'FAISS'},
    #         {'url': 'https://github.com/jbellis/jvector', 'description': 'JVector'},
    #         {'url': 'https://www.jaguardb.com/', 'description': 'Jaguar'},
    #         {'url': 'https://lancedb.com/', 'description': 'LanceDB'},
    #         {'url': 'https://lantern.dev/', 'description': 'Lantern.Dev'},
    #         {'url': 'https://www.marqo.ai/', 'description': 'marqo ai'},
    #         {'url': 'https://milvus.io/', 'description': 'milvus'},
    #         {'url': 'https://www.mongodb.com/products/platform/atlas-vector-search', 'description': 'mongodb'},
    #         {'url': 'https://neo4j.com/labs/genai-ecosystem/vector-search/', 'description': 'neo4jvector'},
    #         {'url': 'https://opensearch.org/platform/search/vector-database.html', 'description': 'opensearch'},
    #         {'url': 'https://pgxn.org/dist/vector/', 'description': 'pgvectors'},
    #         {'url': 'https://www.pinecone.io/', 'description': 'pinecone'},
    #         {'url': 'https://qdrant.tech/', 'description': 'Qdrant'},
    #         {'url': 'https://redis.com/solutions/use-cases/vector-database/', 'description': 'redis'},
    #         {'url': 'https://rockset.com/', 'description': 'Rockset'},
    #         {'url': 'https://www.singlestore.com/', 'description': 'https://www.singlestore.com/'},
    #         {'url': 'https://supabase.com/', 'description': 'supabase'},
    #         {'url': 'https://www.alibabacloud.com/help/en/tair/product-overview/what-is-tair', 'description': 'tair'},
    #         {'url': 'https://cloud.tencent.com/document/product/1709', 'description': 'TencentVectorDB'},
    #         {'url': 'https://www.timescale.com/ai', 'description': 'timescalevector'},
    #         {'url': 'https://vespa.ai/', 'description': 'Vespa'},
    #         {'url': 'https://weaviate.io/', 'description': 'weaviate'},
    #         {'url': 'https://www.getzep.com/', 'description': 'zep'}
    #         # Add more URLs as needed
    #     ]
    #     url_descriptions = [item["description"] for item in url_list]
    #     selection = st.selectbox("Select a Vector Database to chat about...", url_descriptions)
    #     selected_item = next(item for item in url_list if item["description"] == selection)
    #     selected_description = selected_item["description"]
    #     selected_url = selected_item["url"]

        
        # Check if the selected URL has changed or if it's the first time a URL is being selected
        # if "selected_url" not in st.session_state or st.session_state["selected_url"] != selected_url:
        #     st.session_state["url_changed"] = True
        # else:
        #     st.session_state["url_changed"] = False

        # st.session_state["selected_url"] = selected_url
        # st.session_state["selected_description"] = selected_description

# Import required libraries
from dotenv import load_dotenv, find_dotenv
from itertools import zip_longest
import os
import logging
import sys
import pandas as pd

logging.basicConfig(stream=sys.stdout, level=logging.WARN)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

import streamlit as st
from streamlit_chat import message

from sidebar_st import Sidebar
from modules.chat_agent import ChatAgent, ChatAgentRouterQueryEngine, ChatAgentReact
from modules.chathistory import ChatHistory
from modules.references import display_ref
from modules.reader import CustomAirtableReader
from modules.indexer import Indexer
from modules.airtableconfig import INDEX_NAMES, AIRTABLE_CONFIG

# Load environment variables


# Set streamlit page configuration
st.set_page_config(layout="wide", page_title="Chat about Build Club Members")
st.title("Chat about Build Club Members")

# Instantiate the main components
sidebar = Sidebar()
sidebar.sidebar_bg('bolt2.png')

@st.cache_resource(show_spinner='Initializing agent...')
def setupChatAgent():

# with st.status("Setting up chat agent...", expanded=True) as status:
    config = AIRTABLE_CONFIG['BuildBountyMembersGenAI']
    reader = CustomAirtableReader()
    st.session_state['reader']=reader

    # st.write("Setting up db query engine...")
    # index_name = INDEX_NAMES[config['TABLE']]
    indexer = Indexer(reader)

    _ = indexer.db_query_engine

    # st.write("Setting up semantic query engine...")

    _ = indexer.semantic_query_engine

    # st.write("Organizing tools...")
    tools = indexer.tools
    if tools is None or len(tools)<1:
        raise ValueError('No retrieval tool detected, please add a tool for the agent')
    
    # st.write("Creating agent...")
    agent=ChatAgentReact(tools)
    # status.update(label="Agent created.", expanded=False)
    return agent

def initConversation():
    history = ChatHistory()
    history.initialize()
    return setupChatAgent(), history

def load_api_key():
    """
    Loads the OpenAI API key
    """
    user_api_key = st.sidebar.text_input(
        label="#### Your OpenAI API key 👇", placeholder="sk-...", type="password"
    )
    if user_api_key:
        st.sidebar.success("API key loaded from sidebar", icon="🚀")
        return user_api_key

    load_dotenv(override=True)
    if os.getenv("OPENAI_API_KEY") != "":
        st.sidebar.success("API key loaded from .env", icon="🚀")

    return os.getenv("OPENAI_API_KEY")

def show_api_key_missing():
        """
        Displays a message if the user has not entered an API key
        """
        st.markdown(
            """
            <div style='text-align: center;'>
                <h4>Enter your <a href="https://platform.openai.com/account/api-keys" target="_blank">OpenAI API key</a> to start chatting</h4>
            </div>
            """,
            unsafe_allow_html=True,
        )

def api_key_present():
    user_api_key = load_api_key()
    if not user_api_key:
        show_api_key_missing()
        return False
    else:
        os.environ["OPENAI_API_KEY"] = user_api_key
        return True
    
def st_exists(name: str):
    return name in st.session_state and name != ""

# def initConversation():
#     history = ChatHistory()
#     history.initialize()
#     return setupChatAgent(), history

def refresh_data_when_button_clicked():
    refresh_data = st.session_state.get("refresh_data", False)
    if  refresh_data:
         with st.status("Refreshing data, it might take a minute or two...", expanded=True) as status:
            reader = CustomAirtableReader()
            indexer = Indexer(reader)
            indexer._buildVectorStoreIndex_supabase()

def main_processing():
    if not api_key_present():
        return
    # show sidebar
    
    # Initialize the chatbot if first time or the chat history if button clicked
    reset_chat = st.session_state.get("reset_chat", True)
    if  reset_chat or "chatbot" not in st.session_state or "history" not in st.session_state:
            
        chatbot, history = initConversation()
        st.session_state["reset_chat"] = False
        st.session_state["chatbot"] = chatbot
        st.session_state["history"] = history 


    # CHAT

    st.session_state["history"].display_chat_messages_history()
    
    # Accept user input
    if prompt := st.chat_input("Please ask a question..."):
        # Display user message in chat message container
        with st.chat_message("user"):
            st.markdown(prompt)
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            assistant_response, references = st.session_state["chatbot"].chat(prompt)
            message_placeholder.markdown(assistant_response)
            # response = st.write_stream
            if references is not None and len(references)>0:
                display_ref(references)

            
        # Add assistant response to chat history
        st.session_state.messages.append({"role": "assistant", "content": assistant_response, "references": references})


sidebar.show_contact()
sidebar.show_options()
main_processing()
refresh_data_when_button_clicked()


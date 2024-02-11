# Import required libraries
from dotenv import load_dotenv
from itertools import zip_longest
import os

import streamlit as st
from streamlit_chat import message

# Create a Griptape Agent and give it a WebScraper tool
# Use the Chat utility to chat with it.

# from griptape.structures import Agent
# from griptape.tools import WebScraper, TaskMemoryClient
# from griptape.utils import Chat
# from griptape.engines import VectorQueryEngine
# from griptape.loaders import WebLoader
# from griptape.rules import Ruleset, Rule
# from griptape.structures import Agent
# from griptape.tools import VectorStoreClient, BaseTool
# from griptape.utils import Chat
# from griptape.drivers import LocalVectorStoreDriver, OpenAiEmbeddingDriver
# from griptape.drivers import OpenAiChatPromptDriver

from sidebar_st import Sidebar


# Load environment variables
load_dotenv()

# Set streamlit page configuration
st.set_page_config(layout="wide", page_title="Chat about Airtable")
st.title("Chat about Airtable")

# Instantiate the main components
sidebar = Sidebar()

# Initialize session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []  # Store AI generated responses

if 'past' not in st.session_state:
    st.session_state['past'] = []  # Store past user inputs

if 'entered_prompt' not in st.session_state:
    st.session_state['entered_prompt'] = ""  # Store the latest user input


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
# Define function to submit user input
def submit():
    # Set entered_prompt to the current value of prompt_input
    st.session_state.entered_prompt = st.session_state.prompt_input
    # Clear prompt_input
    st.session_state.prompt_input = ""

def api_key_present():
    user_api_key = load_api_key()
    if not user_api_key:
        show_api_key_missing()
        return False
    else:
        os.environ["OPENAI_API_KEY"] = user_api_key
        return True

def configure_vector_tool(namespace: str, url: str, url_description: str):

    # Load documents and build index
    documents = SimpleDirectoryReader(
        "../../examples/data/paul_graham"
    ).load_data()
    index = VectorStoreIndex.from_documents(documents)

    return vector_store_tool


def configure_agent():
    tools = [WebScraper(), TaskMemoryClient(off_prompt=False)]

    # if st_exists("vector_tool"):
    #     tools.append(st.session_state.vector_tool)

    agent = Agent(

        # TO CHANGE THE MODEL
        # prompt_driver=OpenAiChatPromptDriver(
        #     model="gpt-3.5-turbo"
        # ),
        # rulesets=[
        #     Ruleset(
        #         name="Vector Database Expert",
        #         rules=[
        #             Rule(
        #                 "Be truthful. Be specific."
        #             )
        #         ]
        #     )
        # ],
        tools=tools
        )
    return agent

def generate_response(agent:Agent, user_query: str, selected_description: str, selected_url: str):
    """
    Generate AI response using the ChatOpenAI model.
    """
    # Build the list of messages to provide context
    prompt = """Please try your best to answer with precision the following user query. If the question is ambiguous, take an opinionated option and
    always describe your assumptions. Your audience are expert software engineer, so don't answer platitudes such as 'The database is performant for most relevant use cases' which 
    doesn't provide any practical information to the engineer. The engineer needs you to understand whether the selected database can meet their needs.add
    
    The following question related to the selected database {selected_description}, with main website located at {selected_url}.
    
    When using a web search tool, look first in the main website but if no sufficient information is available, use a seach engine to find alternate websites to scrape.
    
    Here's the user query: {user_query}"""

    formatted_prompt = prompt.format(selected_description=selected_description, selected_url=selected_url, user_query=user_query)

    # add to prompt

    response = agent.run(formatted_prompt)

    # Generate response using the chat model
    ai_response = response.output_task.output.to_text()

    return ai_response

def submit_first_description_query(agent:Agent, url:str, url_description: str):

    first_query = """
        For {url_description} {url}, provide a 250 words paragraph of text that highlights the characteristics of this vector database. 
        Provide a summary of the features and use cases."""
    
    user_query = first_query.format(url_description=url_description, url=url)

            # Generate response
    output = generate_response(agent, user_query, selected_description=url_description, selected_url=url)

    # Append AI response to generated responses
    return output

def st_exists(name: str):
    return name in st.session_state and name != ""

def main_processing():
    if not api_key_present():
        return
    
    # Select Vector Database to chat about
    sidebar.url_selector()
    if st.session_state["selected_url"] == "":
        st.write("Please select a database to chat about...")
        return
    
    # Configure vector engine
    namespace = st.session_state["selected_description"]
    if st.session_state["url_changed"]:
        url = st.session_state["selected_url"]
        url_description = st.session_state["selected_description"]
        #st.session_state.vector_tool = configure_vector_tool(namespace, url, url_description)

        st.session_state.agent = configure_agent()

        intro_text = submit_first_description_query(st.session_state.agent, url, url_description)
        print(intro_text)
        st.session_state["intro_text"] = intro_text


    if st_exists("selected_url"):
         st.markdown(f'#### [{st.session_state["selected_url"]}]({st.session_state["selected_url"]})')

    if st_exists("intro_text"):
        st.markdown(f'<div style="border:1px solid #ddd; border-radius: 5px; padding: 10px; margin: 10px 0;">{st.session_state["intro_text"]}</div>', unsafe_allow_html=True)
    
    # Show sidebard

    # Create a text input for user
    st.text_input('YOU: ', key='prompt_input', on_change=submit)


    if st.session_state.entered_prompt != "":
        # Get user query
        user_query = st.session_state.entered_prompt

        # Append user query to past queries
        st.session_state.past.append(user_query)

        # Generate response
        output = generate_response(st.session_state["agent"], user_query, selected_description=st.session_state["selected_description"], selected_url=st.session_state["selected_url"])

        # Append AI response to generated responses
        st.session_state.generated.append(output)

    # Display the chat history (avatar: https://www.dicebear.com/styles/)
    if st.session_state['generated']:
        for i in range(len(st.session_state['generated'])-1, -1, -1):
            # Display AI response
            message(st.session_state["generated"][i], key=str(i), avatar_style="bottts-neutral")
            # Display user message
            message(st.session_state['past'][i],
                    is_user=True, key=str(i) + '_user', avatar_style='pixel-art-neutral')
            
sidebar.show_contact()
main_processing()

# Add credit
st.markdown("""
---
© Isabelle for The Builders Club, Reach out for contributions!""")

import streamlit as st
from modules.references import display_references, display_ref

class ChatHistory:
    
    def __init__(self):
        self.history = st.session_state.get("messages", [])
        st.session_state["messages"] = self.history

    def default_prompt(self):
        return f"Ask me (almost) anything about our Build Club members!"

    def initialize_assistant_history(self):
        st.session_state.messages.append({"role": "assistant", "content": self.default_prompt()})

    def display_chat_messages_history(self):
        # Display chat messages from history
        for message in st.session_state.messages:
            print('history: ---------------------------\n', message, '\n')
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
                if 'references' in message:
                    display_ref(message.get('references', []))

    def initialize(self):
        st.session_state.messages = []
        self.initialize_assistant_history()

    def append(self, mode, message):
        st.session_state["messages"].append({"role": mode, "content": message})
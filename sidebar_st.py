import streamlit as st
import base64

class Sidebar:

    MODEL_OPTIONS = ["gpt-3.5-turbo-16k", "gpt-4"]
    TEMPERATURE_MIN_VALUE = 0.0
    TEMPERATURE_MAX_VALUE = 1.0
    TEMPERATURE_DEFAULT_VALUE = 0.0
    TEMPERATURE_STEP = 0.01

    @staticmethod
    def sidebar_bg(side_bg):

        side_bg_ext = 'png'

        st.markdown(
            f"""
            <style>
            [data-testid="stSidebar"] > div:first-child {{
                background: url(data:image/{side_bg_ext};base64,{base64.b64encode(open(side_bg, "rb").read()).decode()});
            }}
            </style>
            """,
            unsafe_allow_html=True,
            )

    @staticmethod
    def about():
        about = st.sidebar.expander("Talk about Build Club members 🤖")
        sections = [
            "#### Powered by [Llamaindex](https://www.llamaindex.ai/), [Supabase](https://supabase.com/),  [OpenAI](https://platform.openai.com) and [Streamlit](https://github.com/streamlit/streamlit) ⚡",
            "#### Source code: [isisChameleon/airtable-chatbot](https://github.com/IsisChameleon/airtable-chat)",
        ]
        for section in sections:
            about.write(section)

    @staticmethod
    def reset_chat_button():
        if st.button("Reset chat"):
            st.session_state["reset_chat"] = True
        st.session_state.setdefault("reset_chat", False)

    @staticmethod
    def refresh_data_button():
        if st.button("Refresh Data"):
            st.session_state["refresh_data"] = True
        st.session_state.setdefault("refresh_data", False)
        
    @staticmethod
    def on_model_parameters_change_callback():
        st.session_state["tweak"] = True
        
    def show_options(self):
        if "tweak" not in st.session_state:
            st.session_state.tweak = False
        with st.sidebar.expander("⚙️ Tweak Me", expanded=True):

            self.reset_chat_button()
            self.refresh_data_button()

    #Contact
    @staticmethod
    def show_contact():
        
        with st.sidebar.expander("📧 Contact"):

            st.write("**GitHub:** [Build Club Members Chat](https://github.com/IsisChameleon/airtable-chat)")
            st.write("**Made for ** [The Builders Club](https://www.thebuilderclub.org/)")
            st.write("**Contributions or suggestions welcome! ** : isisdesade@gmail.com")

   
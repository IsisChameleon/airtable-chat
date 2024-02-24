import streamlit as st
import pandas as pd

# Sample DataFrame
data = {'Name': ['Alice', 'Bob', 'Charlie'],
        'Age': [25, 30, 35],
        'City': ['New York', 'Los Angeles', 'Chicago']}
df = pd.DataFrame(data)

# Function to display details of the user (this can be customized)
def show_user_details(name):
    st.write(f"Details for {name}")

# Display the DataFrame with buttons
for index, row in df.iterrows():
    cols = st.columns([2, 1, 2, 1]) # Adjust the number of columns and their sizes as needed
    cols[0].write(row['Name'])
    cols[1].write(row['Age'])
    cols[2].write(row['City'])

    # Each button is unique by using the index of the DataFrame's row
    if cols[3].button(f"Details", key=f"button_{index}"):
        # This is where you can redirect to another page or show details
        # For demonstration, I'll just show details on the same page
        show_user_details(row['Name'])

extra_info = {"member_name": "member name bloblo", "linkedin_url": "http://www.example.com"}
extra_info2 = {"member_name": "member name bloblo", "linkedin_url": "http://www.example.com"}
extra_info3 = {"member_name": "member name bloblo", "linkedin_url": "http://www.example.com"}
df1 = pd.DataFrame.from_dict([extra_info, extra_info2, extra_info3])


extra_info2 = {"member_name": "member name bloblo", "build_update": "http://www.example.com"}

def display_references(references):
    st.markdown(references)
if "messages" not in st.session_state:
    st.session_state['messages']=[]
# Run this with 'streamlit run your_script.py'
with st.container():
    tab_chat, tab_explorer = st.tabs(['chat', 'explore'])
    with tab_chat:
        if prompt := st.chat_input("Please ask a question..."):
        # Display user message in chat message container
            with st.chat_message("user"):
                st.markdown(prompt)
        # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
        
            with st.chat_message("assistant"):
                assistant_response = "yoyo assistant reference"
                references = "references blala"
                message_placeholder=st.container()
                with message_placeholder:
                    st.markdown(assistant_response)
                    display_references(references)
    with tab_explorer:
        st.dataframe(df1)

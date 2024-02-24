import streamlit as st
import pandas as pd
from llama_index.core.schema import NodeWithScore, TextNode
from modules.references import display_ref

query_result = [NodeWithScore(node=TextNode(id_='recGbVC3JkYyRrRu1', embedding=None, metadata={'airtable_id': 'recGbVC3JkYyRrRu1', 'skills': ['Go to market', 'Domain expert'], 'member_name': 'Justin Hansky', 'linkedin_url': 'https://www.linkedin.com/in/justin-hansky-70154693/', 'referrer_name': 'N/A', 'keen_for_ai_meetup': True, 'accepted': True, 'record_type': 'build_club_members', 'extracted_timestamp': 1708678935.031194}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text="MEMBER DETAILS:\n\nnMember name: Justin Hansky\nLinkedIn Url: https://www.linkedin.com/in/justin-hansky-70154693/\nSkills: ['Go to market', 'Domain expert']\nBuild Project: We're building an AI powered Monday.com for legal due diligence, helping law firms improve margins and speed to deliver critical client work.\nPast work: I used to work for a no-code app builder being deployed in law firms. Have built apps that help firms better manage a Fortune 500 client's NDA processes. I've also designed and built an app for a firm that gives companies being raided by Government authorities up to the minute advice for managing the situation. This includes bespoke instructions for secretaries, C-suites, heads of legal and IT.\nBuild squad: Yes! Elena Tsalanidis is my co-founder and another ex-lawyer and legaltech veteran.\n", start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), score=10.0), NodeWithScore(node=TextNode(id_='recTu7B2m4sh3NfUE', embedding=None, metadata={'airtable_id': 'recTu7B2m4sh3NfUE', 'skills': ['Backend software dev', 'Front end software dev', 'AI / ML specialist researcher'], 'member_name': 'Joe Jiang', 'linkedin_url': 'https://www.linkedin.com/in/jojo-data/', 'referrer_name': 'N/A', 'keen_for_ai_meetup': True, 'accepted': True, 'record_type': 'build_club_members', 'extracted_timestamp': 1708678935.0317123}, excluded_embed_metadata_keys=[], excluded_llm_metadata_keys=[], relationships={}, text='MEMBER DETAILS:\n\nnMember name: Joe Jiang\nLinkedIn Url: https://www.linkedin.com/in/jojo-data/\nSkills: [\'Backend software dev\', \'Front end software dev\', \'AI / ML specialist researcher\']\nBuild Project: "Problem: Contract summaries are simplified and condensed overviews of contract that emphasis the essential information in a straightforward and comprehensible format, widely used in companies\' contracts approval process, transaction due diligence reports and can assist non-lawyers to grasp the main contractual obligations. The problem faced by many in-house lawyers and contract administrators is that the process of creating contract summaries is often a time-consuming and laborious task, especially for complex contracts with lengthy clauses and legal jargon. Solution: Our solution constitutes an AI-powered contract summarisation tool that conducts automatic analysis and summarisation of legal contracts by extracting essential commercial terms and presenting them in a readily comprehensible format."\nPast work: fully automated data pipelines and state-of-art data platforms\nBuild squad: Harriet Liu\nExpectation from joining the club: In the next six weeks, our primary goal is to elevate our current prototype into a more mature and refined version of our contract summarisation solution. We have ambitious plans to make significant progress during this period, focusing on the following key objectives:\n\n1. Performance Optimisation: During this period, we will dedicate resources to performance optimisation, reducing latency, and streamlining the platform\'s overall responsiveness. Our aim is to create a seamless user experience that delivers results promptly and efficiently.\n2. Comprehensive Testing: Rigorous testing is paramount to our development process. We will conduct extensive testing, both internally and with selected users, to identify and address any potential issues, ensuring a stable and reliable platform.\n3. User Interface Refinement: Understanding the importance of an intuitive and user-friendly interface, we will prioritize refining the user experience. By incorporating valuable feedback from legal professionals and beta testers, we aim to create a platform that seamlessly fits into lawyers\' real-life workflows, enhancing their productivity and efficiency.\n4. Expand Contract Type Coverage: Building on our existing eight contract types, we aim to broaden the coverage to encompass an even more diverse range of contract formats. Our goal is to enhance the platform\'s versatility, ensuring it can efficiently handle an extensive array of legal agreements encountered by in-house lawyers and business managers.\nLocation: Sydney', start_char_idx=None, end_char_idx=None, text_template='{metadata_str}\n\n{content}', metadata_template='{key}: {value}', metadata_seperator='\n'), score=10.0)]

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
    
# with st.container():
#     tab_chat, tab_explorer = st.tabs(['chat', 'explore'])
#     with tab_chat:
#         if prompt := st.chat_input("Please ask a question..."):
#         # Display user message in chat message container
#             with st.chat_message("user"):
#                 st.markdown(prompt)
#         # Add user message to chat history
#             st.session_state.messages.append({"role": "user", "content": prompt})
        
#             with st.chat_message("assistant"):
#                 assistant_response = "yoyo assistant reference"
#                 references = "references blala"
#                 message_placeholder=st.container()
#                 with message_placeholder:
#                     st.markdown(assistant_response)
#                     display_references(references)
#     with tab_explorer:
#         st.dataframe(df1)
    
display_ref(query_result)

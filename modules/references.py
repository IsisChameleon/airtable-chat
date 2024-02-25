# Import required libraries
from dotenv import load_dotenv, find_dotenv
from itertools import zip_longest
from typing import List
import os
import logging
import sys
from llama_index.core.schema import NodeWithScore
import pandas as pd

from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv(), override=True)

SUPABASE_CONNECTION_STRING=os.getenv('SUPABASE_CONNECTION_STRING')
SQLITE_MEMORY_CONNECTION_STRING="sqlite:///:memory:"
DB_CONNECTION=SUPABASE_CONNECTION_STRING

#https://chartio.com/resources/tutorials/how-to-execute-raw-sql-in-sqlalchemy/
from sqlalchemy import (
    insert,
    create_engine,
    MetaData,
    Table,
    Column,
    String,
    Boolean,
    Integer,
    select,
    column,
)

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from modules.reader import CustomAirtableReader
from pyairtable import Table, Api, Base
from modules.airtableconfig import AIRTABLE_CONFIG
api = Api(AIRTABLE_CONFIG['BuildBountyMembersGenAI']['TOKEN'])
base_id = AIRTABLE_CONFIG['BuildBountyMembersGenAI']['BASE']
member_table_id = AIRTABLE_CONFIG['BuildBountyMembersGenAI']['TABLE']
build_update_table_id = AIRTABLE_CONFIG['BuildBountyBuildUpdates']['TABLE']

import io
import streamlit as st
from streamlit_chat import message
import re

#TODO clean up this mess of extra code

def display_references(references):
    if references is not None and len(references)>1:
        source_placeholder=st.empty()
        source_placeholder.markdown(references)

# def format_newlines_for_markdown(s):
#     # Step 1: Replace "\n\n" with a temporary placeholder
#     s = re.sub(r'\n\n', 'TEMP_NEWLINE_PLACEHOLDER', s)

#     # Step 2: Replace "\n" with "\n  "
#     s = re.sub(r'\n', '\n  ', s)

#     # Step 3: Replace the temporary placeholder with "\n\n  "
#     s = re.sub('TEMP_NEWLINE_PLACEHOLDER', '\n\n  ', s)

#     print("Improved text:",  s)

#     return s

# # Example usage
# original_string = "This is a test string.\nIt contains newlines.\n\nAnd double newlines."
# formatted_string = format_newlines_for_markdown(original_string)
# print(formatted_string)


def get_profile_picture(name):
    engine = create_engine(DB_CONNECTION, pool_pre_ping=True)
    with engine.connect() as connection:
        result = connection.execute(
            "SELECT profile_picture FROM build_club_members WHERE name = %s", (name,)
        )
        picture = result.fetchone()
        return picture[0] if picture else None

def display_profile_picture(name):
        picture_binary = get_profile_picture(name)
        if picture_binary:
            # Convert binary data to bytes
            picture_bytes = io.BytesIO(picture_binary)

            # Display the image
            st.image(picture_bytes)
        else:
            st.write("No profile picture found for this name.")

def str_get_from(text, start):
    start_index=text.find(start)
    if start_index == -1:
        return text
    return text[start_index:]

@st.cache_data
def get_member_info(rec_id: str):
    member_table = api.table(base_id, member_table_id)
    print(f"Loading member info for rec_id:{rec_id}")
    member_record = member_table.get(rec_id)
    # TODO save reader in session state?
    reader = CustomAirtableReader()
    metadata, semantic_info = reader.extract_metadata_member(member_record)
    image_url = reader.get_image_url_from_member_record(member_record)
    return metadata, semantic_info, image_url

@st.cache_data
def get_build_update_info(rec_id: str):
    build_update_table = api.table(base_id, build_update_table_id)
    print(f"Loading build update info for rec_id:{rec_id}")
    build_update_record = build_update_table.get(rec_id)
    reader = CustomAirtableReader()
    metadata, semantic_info = reader.extract_metadata_build_update(build_update_record)

    member_rows = reader.find_member_by_name(metadata['member_name'])
    if member_rows is not None and len(member_rows)>0:
        member_row=member_rows[0]
        member_id=member_row[0][0]
        member_table = api.table(base_id, member_table_id)
        print(f"Loading member info for rec_id:{member_id}")
        member_record = member_table.get(member_id)
    image_url=''
    if member_record:
        image_url = reader.get_image_url_from_member_record(member_record)
    return metadata, semantic_info, image_url

def display_ref(nodes_with_score: List[NodeWithScore]):

    if nodes_with_score is None:
        return

    for node in nodes_with_score:
        print(f'=====================metadata keys: {node.node.metadata.keys()}')
        # ['airtable_id', 'skills', 'member_name', 'linkedin_url', 'referrer_name', 'keen_for_ai_meetup', 'accepted', 'record_type', 'extracted_timestamp']
        metadata = node.node.metadata.copy()  # Copy metadata dictionary
        if metadata is None or metadata == {} or metadata.get('airtable_id', '')=='':
            next

        if metadata.get('record_type')=='build_club_members':
            metadata, semantic_info, image_url = get_member_info(metadata['airtable_id'])
            linkedin_url = metadata.get('linkedin_url', '')
            
            with st.container(border = True):
                cols = st.columns([3, 1, 8])
                with cols[0]:
                    st.markdown(f"#### [{metadata['member_name']}]({linkedin_url})")
                    if image_url != '':
                        st.image(image_url, use_column_width='auto')

                with cols[2]:
                    st.write(f"**{','.join(metadata.get('skills', []))}**")
                    st.write()
                    st.markdown(semantic_info.get('build_project', ''))
                    st.markdown(semantic_info.get('past_work', ''))

        if metadata.get('record_type')=='build_updates':
            metadata, semantic_info, image_url = get_build_update_info(metadata['airtable_id'])

            with st.container(border = True):
                cols = st.columns([3, 1, 8])
                with cols[0]:
                    st.markdown(f"#### {metadata['member_name']}")
                    if image_url != '':
                        st.image(image_url, use_column_width='auto')

                with cols[2]:
                    st.markdown(f"From build update **{metadata['build_update_date'][:10]}**")
                    project_name = metadata['project_name']
                    if project_name != '':
                        st.markdown(f"For project {project_name}")
                    st.write()
                    st.markdown(semantic_info.get('build_this_week', ''))
                    st.markdown(semantic_info.get('build_url',''))
                    st.markdown(semantic_info.get('milestone', ''))

# def display_ref2(nodes_with_score: List[NodeWithScore]):

#     if nodes_with_score is None:
#         return
#     # Prepare a list to hold each row's data
#     data = []

#     # Extracting data from each NodeWithScore object
#     for node in nodes_with_score:
#         print(f'=====================metadata keys: {node.node.metadata.keys()}')
#         row_data = node.node.metadata.copy()  # Copy metadata dictionary
#         if row_data is None or row_data == {}:
#             next

#         if row_data.get('record_type')=='build_club_members':
#             member_table = api.table(base_id, member_table_id)
#             print(f"row_data['airtable_id'] {row_data['airtable_id']}")
#             member_record = member_table.get(row_data['airtable_id'])
#             reader = CustomAirtableReader()
#             metadata = reader.extract_metadata_member(member_record)

#             st.subheader(metadata['member_name'])
#             st.image(metadata['profile_picture_url'])
#             st.markdown(node.node.text)


            
#         # if row_data.get('record_type')=='build_updates':
#         #     build_updates_table = api.table(base_id, build_update_table_id)

#         # row_data['text'] = node.node.text     # Add text property to the dictionary
#         # data.append(row_data)


#     # Create DataFrame
#     df = pd.DataFrame(data)

#     # Display the DataFrame without the 'text' column
#     st.write(df.drop(columns=['text']))

#     # Iterate over each row to add buttons and display text if clicked
#     for index, row in df.iterrows():
#         # Generate a unique key for each button (important for correct functioning)
#         button_key = f"button_{index}"

#         # Add a button for each row
#         if st.button('Show Text', key=button_key):
#             # Display the text below the row if button is clicked
#             # st.text("Text for Row {}: {}".format(index, row['text']))
#             #         if st.button('Show Details', key=button_key):
#             # Streamlit columns for layout
#             col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed

#             name = row['name']

#             with col1:
#                 # Display the image in the left column
#                 display_profile_picture(name)
#             with col2:
#                 # Display the text in the right column
#                 st.write(row['text'])

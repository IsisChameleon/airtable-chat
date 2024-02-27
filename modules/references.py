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

logging.basicConfig(stream=sys.stdout, level=logging.WARN)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

from modules.reader import CustomAirtableReader
from pyairtable import Table, Api, Base
from modules.airtableconfig import AIRTABLE_CONFIG
api = Api(AIRTABLE_CONFIG['BuildBountyMembersGenAI']['TOKEN'])
base_id = AIRTABLE_CONFIG['BuildBountyMembersGenAI']['BASE']
member_table_id = AIRTABLE_CONFIG['BuildBountyMembersGenAI']['TABLE']
build_update_table_id = AIRTABLE_CONFIG['BuildBountyBuildUpdates']['TABLE']
from modules.reader import  BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS

import io
import streamlit as st
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
def find_by_name(member_name: str) -> dict:
    member_rows = CustomAirtableReader.find_member_by_name(member_name)
    if member_rows is not None and len(member_rows)>0:
        member_row=member_rows[0]
        member_id=member_row[0]
        member_table = api.table(base_id, member_table_id)
        print(f"Loading member info for rec_id:{member_row} {member_id}")
    member_record=''
    try:
        member_record = member_table.get(member_id)
    except:
        pass
    return member_record

@st.cache_data
def get_build_update_info(rec_id: str):
    build_update_table = api.table(base_id, build_update_table_id)
    print(f"Loading build update info for rec_id:{rec_id}")
    build_update_record = build_update_table.get(rec_id)
    reader = CustomAirtableReader()
    metadata, semantic_info = reader.extract_metadata_build_update(build_update_record)
    member_record = find_by_name(metadata['member_name'])
    image_url=''
    if member_record != '':
        image_url = reader.get_image_url_from_member_record(member_record)
    return metadata, semantic_info, image_url, member_record

def display_ref(nodes_with_score: List[NodeWithScore]):

    if nodes_with_score is None:
        return
    
    build_updates=[]

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
            metadata_2, semantic_info, image_url, member_record = get_build_update_info(metadata['airtable_id'])

            build_updates.append({
                "name": member_record['fields']['Name'],
                "metadata": metadata,
                "image_url": image_url,
                "semantic_info": semantic_info,
                "member_record": member_record
            })

    name=''
    sorted_build_updates = sorted(build_updates, key=lambda x: (x["name"]))
    for build_update in sorted_build_updates:
        print(f'About to show {build_update["name"]}: {build_update}')
        semantic_info = build_update['semantic_info']
        metadata = build_update['metadata']
        image_url = build_update['image_url']

        if build_update["name"]!=name:
            print("New name")
            name = build_update["name"]
            current_container = st.container(border=True)
            cols = current_container.columns([3, 1, 8])

            fields=member_record.get('fields', {})
            print('********* fields:' , fields)
            skills=fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['skills'], [])
            print('********* skills:' , skills)
            linkedin_url = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['linkedin_url'], '')
            print('********* skills:' , linkedin_url)
            cols[0].markdown(f"#### [{metadata['member_name']}]({linkedin_url})")
            if image_url != '':
                cols[0].image(image_url, use_column_width='auto')


            cols[2].write(f"**{','.join(skills)}**")
            cols[2].write()
            cols[2].markdown(f"From build update **{metadata['build_update_date'][:10]}**")
            project_name = metadata['project_name']
            if project_name != '':
                cols[2].markdown(f"For project {project_name}")
            cols[2].write()
            cols[2].markdown(semantic_info.get('build_this_week', ''))
            cols[2].markdown(semantic_info.get('build_url',''))
            cols[2].markdown(semantic_info.get('milestone', ''))

        else:
            print("Same name")
            cols[2].write()
            cols[2].markdown(f"From build update **{metadata['build_update_date'][:10]}**")
            cols[2].write()
            cols[2].markdown(semantic_info.get('build_this_week', ''))
            cols[2].markdown(semantic_info.get('build_url',''))
            cols[2].markdown(semantic_info.get('milestone', ''))

# def display_ref_old(nodes_with_score: List[NodeWithScore]):

#     if nodes_with_score is None:
#         return

#     for node in nodes_with_score:
#         print(f'=====================metadata keys: {node.node.metadata.keys()}')
#         # ['airtable_id', 'skills', 'member_name', 'linkedin_url', 'referrer_name', 'keen_for_ai_meetup', 'accepted', 'record_type', 'extracted_timestamp']
#         metadata = node.node.metadata.copy()  # Copy metadata dictionary
#         if metadata is None or metadata == {} or metadata.get('airtable_id', '')=='':
#             next

#         if metadata.get('record_type')=='build_club_members':
#             metadata, semantic_info, image_url = get_member_info(metadata['airtable_id'])
#             linkedin_url = metadata.get('linkedin_url', '')
            
#             with st.container(border = True):
#                 cols = st.columns([3, 1, 8])
#                 with cols[0]:
#                     st.markdown(f"#### [{metadata['member_name']}]({linkedin_url})")
#                     if image_url != '':
#                         st.image(image_url, use_column_width='auto')

#                 with cols[2]:
#                     st.write(f"**{','.join(metadata.get('skills', []))}**")
#                     st.write()
#                     st.markdown(semantic_info.get('build_project', ''))
#                     st.markdown(semantic_info.get('past_work', ''))

#         if metadata.get('record_type')=='build_updates':
#             metadata, semantic_info, image_url = get_build_update_info(metadata['airtable_id'])

#             with st.container(border = True):
#                 cols = st.columns([3, 1, 8])
#                 with cols[0]:
#                     st.markdown(f"#### {metadata['member_name']}")
#                     if image_url != '':
#                         st.image(image_url, use_column_width='auto')

#                 with cols[2]:
#                     st.markdown(f"From build update **{metadata['build_update_date'][:10]}**")
#                     project_name = metadata['project_name']
#                     if project_name != '':
#                         st.markdown(f"For project {project_name}")
#                     st.write()
#                     st.markdown(semantic_info.get('build_this_week', ''))
#                     st.markdown(semantic_info.get('build_url',''))
#                     st.markdown(semantic_info.get('milestone', ''))


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

import io
import streamlit as st
from streamlit_chat import message

def display_references(references):
    if references is not None and len(references)>1:
        source_placeholder=st.empty()
        source_placeholder.markdown(references)

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

def display_ref(nodes_with_score: List[NodeWithScore]):

    if nodes_with_score is None:
        return
    # Prepare a list to hold each row's data
    data = []

    # Extracting data from each NodeWithScore object
    for node in nodes_with_score:
        row_data = node.node.metadata.copy()  # Copy metadata dictionary
        row_data['text'] = node.node.text     # Add text property to the dictionary
        data.append(row_data)

    # Create DataFrame
    df = pd.DataFrame(data)

    # Display the DataFrame without the 'text' column
    st.write(df.drop(columns=['text']))

    # Iterate over each row to add buttons and display text if clicked
    for index, row in df.iterrows():
        # Generate a unique key for each button (important for correct functioning)
        button_key = f"button_{index}"

        # Add a button for each row
        if st.button('Show Text', key=button_key):
            # Display the text below the row if button is clicked
            # st.text("Text for Row {}: {}".format(index, row['text']))
            #         if st.button('Show Details', key=button_key):
            # Streamlit columns for layout
            col1, col2 = st.columns([1, 3])  # Adjust the ratio as needed

            name = row['name']

            with col1:
                # Display the image in the left column
                display_profile_picture(name)
            with col2:
                # Display the text in the right column
                st.write(row['text'])

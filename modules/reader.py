"""Airtable reader."""
from typing import List

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document, BaseNode, TextNode
from pyairtable import Table, Api, Base
import pandas as pd
import json
import uuid
import logging
import os

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

BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS = {
    "skills": "What are your areas of expertise you have (select max 4 please)",
    "name": "Name",
    "linkedin_url": "What's the link to your LinkedIn?",
    "build_project": "What will you build",
    "past_work": "Past work",
    "are_you_building_in_squad": "Optional — building with a squad?",
    "based_in_sydney": "Where are you based? (note only Sydney residents accepted)",
    "expectation_from_joining_club": 'What do you want to get out of this program?',
    "phone_number": "Phone number (to add to WhatsApp group",
    "member_location": "Location",
    "profile_picture_url": "Profile picture",
    "member_acceptance_in_club": "Final decision",
    "referee": "Referred by a builder? Tell us who so we can hit them up with some build points",
    "referrer_name": "Refer name",
    "assignee": "Assignee",
    "status" :"Status",
    "ai_builder_linkedin_badge": "Are you able and willing to add Aura AI Builder Fellow as a badge on your LinkedIn to recognise the program?",
    "best_time_for_build_sessions": "Do you have a preference time/ day? Please select all you can do",
    "keen_for_ai_meetup": "We would love to extend an invitation to an intimate AI meetup we are holding. If you are successful, we will also be doing a quick cohort induction prior"
}

WITH_A_TEAM_TPL = """.My team is {are_you_building_in_squad}"""

NODE_TPL = """
My name is {name}, and my linkedin profile is {linkedin_url}. 
My skills include {skills}.
I am currently building {build_project} {with_a_team}.
In the past I worked on {past_work}.
I'm hoping that joining the club will allow me to {expectation_from_joining_club}
My location is {location}
I'm available for building on {best_time_for_build_sessions}

"""

#'Name (from Notes)'
#'Full Name (from Referred by a builder? Tell us who so we can hit them up with some build points)'


class CustomAirtableReader(BaseReader):
    """Airtable reader. Reads data from a table in a base.

    Args:
        api_key (str): Airtable API key.
    """

    def __init__(self, api_key: str, base_id: str, table_id: str) -> None:
        """Initialize Airtable reader."""

        self.api = Api(api_key)
        self.base_id = base_id
        self.table_id = table_id 
        self._data = None
        self._fields = None

    @property
    def data(self, reload=False):
        if (self._data is None or reload==True): 
            self._data = self._load_data()
        return self._data
    
    @property
    def fields(self, reload=False):
        reloaded = False
        if (self._data is None or reload==True): 
            self._data = self._load_data()
            reloaded=True
        if (self._fields is None or reloaded==True):
            all_records = self._data
            self._fields = [record.get("fields", {}) for record in all_records]
        return self._fields

    def _load_data(self) -> List[dict]:
        table = self.api.table(self.base_id, self.table_id)
        self._data = table.all()
        return self._data
    
    def extract_documents(self) -> List[Document]:

        # if (self.data is None): 
        #     _ = self._load_data()

        all_records = self.data

        # Extract the 'fields' content from each element
        fields = [item['fields'] for item in all_records]

        documents = []
        for field in fields:
            # Copy the fields dictionary to extra_info
            extra_info = field.copy()

            # Keys to be removed from text and metadata (we just don't care about it)
            keys_to_remove = ['Profile picture']
            for key in keys_to_remove:
                extra_info.pop(key, None)  # The None argument ensures no error if the key doesn't exist

            text_dict = extra_info.copy()

            keys_to_remove = ['What will you build']

            # Remove the keys from extra_info if they exist
            for key in keys_to_remove:
                extra_info.pop(key, None)  # The None argument ensures no error if the key doesn't exist

            # Now extra_info contains the fields data without the specified keys
            # print(extra_info)

            text_for_node = json.dumps(text_dict, indent=2)
            print(text_for_node)

            document = Document(text=text_for_node, extra_info=extra_info)
            documents.append(document)

        return documents
    
    def extract_documents_full(self) -> List[Document]:

        # if (self.data is None): 
        #     _ = self._load_data()

        all_records = self.data

        # Extract the 'fields' content from each element
        fields = [item['fields'] for item in all_records]

        documents = []
        for record in all_records:
            field = record['fields']
            print("===FIELD===")
            print(field)
            # Copy the fields dictionary to extra_info
            extra_info = field.copy()
            extra_info['id'] = record['id']

            # Keys to be removed from text and metadata (we just don't care about it)
            keys_to_remove = ['Profile picture']
            for key in keys_to_remove:
                extra_info.pop(key, None)  # The None argument ensures no error if the key doesn't exist

            # Formatting the node text

            build_in_squad = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['are_you_building_in_squad'], '')
            with_a_team = f".My team is {build_in_squad}" if build_in_squad != '' else ''
            location = 'Sydney' if field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['based_in_sydney'], 'No') == 'Yes' else field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['member_location'], 'unknown')
            name = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['name'],'unknown')
            linkedin_url = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['linkedin_url'],'unknown')
            skills = ",".join(field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['skills'],[]))
            build_project = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['build_project'],'nothing')
            past_work = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['past_work'],'unspecified projects')
            expectation_from_joining_club = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['expectation_from_joining_club'],'do well')
            best_time_for_build_sessions = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['best_time_for_build_sessions'], 'unspecified times')
            node_text =  f"""My name is {name}, and my linkedin profile is {linkedin_url}. 
My skills include {skills}.
I am currently building {build_project} {with_a_team}.
In the past I worked on {past_work}.
I'm hoping that joining the club will allow me to {expectation_from_joining_club}
My location is {location}
I'm available for building on {best_time_for_build_sessions}"""
            
            # Removing "semantic" information  from metadata
               
            keys_to_remove_from_metadata = [BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['build_project'],
                                            BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['expectation_from_joining_club'],
                                            BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['best_time_for_build_sessions'],
                                            BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['are_you_building_in_squad'],
                                            BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['are_you_building_in_squad'],
                                            BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['past_work']]

            for key in keys_to_remove_from_metadata:
                extra_info.pop(key, None)  # The None argument ensures no error if the key doesn't exist

            member_accepted_list = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['member_acceptance_in_club'],[])
            accepted=False
            if len(member_accepted_list)>0:
                if 'Accept' in member_accepted_list:
                    accepted=True
            extra_info['accepted']=accepted

            # Update the metadata keys to the short version in BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS
            transformed_metadata = {key: extra_info[value] for key, value in BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS.items() if extra_info.get(value, None) is not None}

            # Now extra_info contains the fields data without the specified keys
            print('===NODE===')
            print(node_text)
            print('===EXTRA_INFO===')
            print(transformed_metadata)

            document = Document(text=node_text, extra_info=transformed_metadata)
            documents.append(document)

        return documents

    def extract_nodes(self) -> List[BaseNode]:
        documents = self.extract_documents_full()

        nodes = [ TextNode(text=d.text, metadata=d.metadata) for d in documents]
        for node in nodes:
            record_id = node.metadata.get('id', '') #metadata['id'] should contain the id of the corresponding record in the airtable table
            if record_id != '':
                node.id_=record_id
        return nodes
    
    def extract_skills(self) -> set:
        all_skills = set()
        for record in self.data:
            fields = record.get("fields", {})
            print(fields.get("Name", "Unknown name"), fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS["skills"], "No skills"))
            skills = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS["skills"], [])
            all_skills.update(skills)
        return all_skills
    
    def extract_rows(self) -> List[dict]:

        transformed = []
        all_records = self.data
        for record in all_records:
            fields = record.get("fields", {})
            skills = fields.get("What are your areas of expertise you have (select max 4 please)", [])
            transformed_detail = {
                "id": record.get("id", str(uuid.uuid4())),
                "member_name": fields.get("Name", ""),
                "linkedin_url": fields.get("What's the link to your LinkedIn?", ""),
                "skill_1": skills[0] if len(skills)>0 else "",
                "skill_2": skills[1] if len(skills)>1 else "",
                "skill_3": skills[2] if len(skills)>2 else "",
                "skill_4": skills[3] if len(skills)>3 else "",
                "build_project": fields.get("What will you build", ""),
            }
            print(json.dumps(transformed_detail, indent=2))
            transformed.append(transformed_detail)
        return transformed
    
    def extract_rows2(self) -> List[dict]:

        transformed = []
        all_records = self.data
        for record in all_records:
            fields = record.get("fields", {})
            skills = fields.get("What are your areas of expertise you have (select max 4 please)", [])
            transformed_detail = {}
            for key in BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS.keys():
                if key=="skills":
                    skills = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS[key], [])
                    transformed_detail["skill_1"]=skills[0] if len(skills)>0 else ""
                    transformed_detail["skill_2"]=skills[1] if len(skills)>1 else ""
                    transformed_detail["skill_3"]=skills[2] if len(skills)>2 else ""
                    transformed_detail["skill_4"]=skills[3] if len(skills)>3 else ""
                elif key=="member_acceptance_in_club":
                    acceptance = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS[key], [])
                    transformed_detail["member_acceptance_in_club"]=True if 'Accept' in acceptance else False
                else:
                    transformed_detail[key]=fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS[key], "")
                    if type(transformed_detail[key]) == list:
                        logging.log(logging.INFO, f'===FIELD IS A LIST=== {key}:{transformed_detail[key]} transforming to string')
                        transformed_detail[key] = str(transformed_detail[key])
            transformed_detail["id"]=record.get("id", str(uuid.uuid4()))

            # remove unwanted keys

            unwanted_keys = ['profile_picture_url']

            for unwanted in unwanted_keys:
                transformed_detail.pop(unwanted, "No problem")

            logging.log(logging.INFO, f"==ROW==:\n{json.dumps(transformed_detail, indent=2)}")
            transformed.append(transformed_detail)
        return transformed
        
    def get_airtable_df(self, base_id: str, table_id: str)-> pd.DataFrame:

        # if (self.data is None): 
        #     _ = self._load_data()

        all_records = self.data

        # Extract the 'fields' content from each element
        fields = [item['fields'] for item in all_records]

        # Create a DataFrame from the extracted 'fields'
        df = pd.DataFrame(fields)

        return df
    
    def refresh_table(self):
        engine = create_engine(DB_CONNECTION)

        # Initialize metadata
        metadata = MetaData()

        # Reflect the table
        build_club_members = Table('build_club_members', metadata, autoload_with=engine)

        rows = self.extract_rows2()

        for row in rows:
            stmt = insert(build_club_members).values(**row)
            with engine.begin() as connection:
                cursor = connection.execute(stmt)
        logging.log(logging.INFO, f'===YAY=== All rows inserted in build_club_members table')
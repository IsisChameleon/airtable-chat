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
import time
from modules.airtableconfig import AIRTABLE_CONFIG

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
    LargeBinary,
    Integer,
    select,
    column,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func

Base = declarative_base()

import requests
def download_image(url: str):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        response.raise_for_status()

BUILD_CLUB_BUILD_UPDATES_AIRTABLE_COLUMNS = {
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

BUILD_UPDATES_AIRTABLE_COLUMNS = {
    "member_name": 'Full name',
    "build_project_name": "😊 Build project name",
    "project_name": "Project",
    "build_this_week": "🏗 Build goal for week",
    "build_url": "🚢 Build URL",
    "slack_email": "Slack",
    "ask_for_community": '🙋\u200d♀️ Any asks?',
    'comments': 'Other comments',
    "build_update_date": "Build update date",
    "help_request": "Would you like to submit a help request or have any asks from community?",
    "number_of_customers_engaged": "How many customers did you test with this week?",
    "milestone": 'Tell us more about the milestone (key learnings)',
    'build_video_demo_available': 'Video attachment of build update',
    "how_close_to_first_paid_customer": 'How close am I to first paid customer?'
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

    def __init__(self) -> None:
        """Initialize Airtable reader."""

        self.api = Api(AIRTABLE_CONFIG['BuildBountyMembersGenAI']['TOKEN'])
        self.base_id = AIRTABLE_CONFIG['BuildBountyMembersGenAI']['BASE']
        self.member_table_id = AIRTABLE_CONFIG['BuildBountyMembersGenAI']['TABLE']
        self.build_update_table_id = AIRTABLE_CONFIG['BuildBountyBuildUpdates']['TABLE']
        self._member_data = None
        self._build_update_data = None
        self._fields = None

    @property
    def member_data(self, reload=False):
        if (self._member_data is None or reload==True): 
            self._member_data = self._load_member_data()
        return self._member_data
    
    @property
    def build_update_data(self, reload=False):
        if (self._build_update_data is None or reload==True): 
            self._build_update_data = self._load_build_update_data()
        return self._build_update_data
    
    @property
    def fields(self, reload=False):
        reloaded = False
        if (self._member_data is None or reload==True): 
            self._member_data = self._load_member_data()
            reloaded=True
        if (self._fields is None or reloaded==True):
            all_records = self._member_data
            self._fields = [record.get("fields", {}) for record in all_records]
        return self._fields

    def _load_member_data(self) -> List[dict]:
        table = self.api.table(self.base_id, self.member_table_id)
        self._member_data = table.all()
        return self._member_data
    
    def _load_build_update_data(self) -> List[dict]:
        table = self.api.table(self.base_id, self.build_update_table_id)
        self._build_update_data = table.all()
        return self._build_update_data
    
    @staticmethod
    def extract_metadata_member(record):
        field = record['fields']

        # METADATA
        extra_info = {}
        extra_info['airtable_id'] = record['id']
        skills = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['skills'],[])
        extra_info['skills'] = skills
        extra_info['member_name'] = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['name'],'Unknown member name')
        linkedin_url = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['linkedin_url'],'')
        extra_info['linkedin_url']=linkedin_url
        referrer_name = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['referrer_name'],'')
        extra_info['referrer_name']=referrer_name
        extra_info['keen_for_ai_meetup']=field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['keen_for_ai_meetup'], False)
        
        member_accepted_list = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['member_acceptance_in_club'],[])
        accepted=False
        if len(member_accepted_list)>0:
            if 'Accept' in member_accepted_list:
                accepted=True
        extra_info['accepted']=accepted
        extra_info['record_type']='build_club_members'
        location = 'Sydney' if field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['based_in_sydney'], 'No') == 'Yes' else field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['member_location'], '')
        extra_info['location']=location

        # TODO maybe not keep this here?
        build_in_squad = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['are_you_building_in_squad'], '')
        build_project = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['build_project'],'')
        past_work = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['past_work'],'')
        expectation_from_joining_club = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['expectation_from_joining_club'],'')
        best_time_for_build_sessions = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['best_time_for_build_sessions'], '')
        semantic_info = { 
            'build_project': build_project, 
            'past_work': past_work,
            'build_in_squad': build_in_squad,
            'expectation_from_joining_club': expectation_from_joining_club,
            'best_time_for_build_sessions': best_time_for_build_sessions
            }

        return extra_info, semantic_info

    def  _extract_member_documents(self):     
    
        all_records = self.member_data

        documents = []
        for record in all_records:
            field = record['fields']
            logging.log(logging.DEBUG, f"===FIELD EXTRACTED FROM AIRTABLE===\n {field}")

            # METADATA
            # extra_info = {}
            # extra_info['airtable_id'] = record['id']
            # skills = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['skills'],[])
            # extra_info['skills'] = skills
            # extra_info['member_name'] = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['name'],'Unknown member name')
            # linkedin_url = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['linkedin_url'],'')
            # extra_info['linkedin_url']=linkedin_url
            # referrer_name = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['referrer_name'],'')
            # extra_info['referrer_name']=referrer_name
            # extra_info['keen_for_ai_meetup']=field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['keen_for_ai_meetup'], False)
            
            # member_accepted_list = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['member_acceptance_in_club'],[])
            # accepted=False
            # if len(member_accepted_list)>0:
            #     if 'Accept' in member_accepted_list:
            #         accepted=True
            # extra_info['accepted']=accepted
            # extra_info['record_type']='build_club_members'

            extra_info, semantic_info = self.extract_metadata_member(record)

            skills = extra_info['skills']
            linkedin_url=extra_info['linkedin_url']
            build_project=semantic_info['build_project']
            past_work=semantic_info['past_work']
            build_in_squad=semantic_info['build_in_squad']
            expectation_from_joining_club=semantic_info['expectation_from_joining_club']
            location=extra_info['location']
            best_time_for_build_sessions=semantic_info['best_time_for_build_sessions']


            # Formatting the node text

            # build_in_squad = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['are_you_building_in_squad'], '')
            # location = 'Sydney' if field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['based_in_sydney'], 'No') == 'Yes' else field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['member_location'], '')
            # name =  extra_info['member_name']
            # linkedin_url = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['linkedin_url'],'')
            # build_project = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['build_project'],'')
            # past_work = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['past_work'],'')
            # expectation_from_joining_club = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['expectation_from_joining_club'],'')
            # best_time_for_build_sessions = field.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['best_time_for_build_sessions'], '')

            node_text = 'MEMBER DETAILS:\n\n'
            node_text+=f"Member name: {extra_info['member_name']}\n"
            if linkedin_url != '':
                node_text+=f"LinkedIn Url: {linkedin_url}\n"
            if skills != '':
                node_text+=f"Skills: {skills}\n"
            node_text+=f"Build Project: {build_project}\n"
            if past_work != '':
                node_text+=f"Past work: {past_work}\n" 
            if build_in_squad != '':
                node_text+=f"Build squad: {build_in_squad}\n" 
            if expectation_from_joining_club != '':
                node_text+=f"Expectation from joining the club: {expectation_from_joining_club}\n"
            if location != '':
                node_text+=f"Location: {location}"
            if best_time_for_build_sessions != '':
                node_text+=f"Best time to build: {best_time_for_build_sessions}"
            
            logging.log(logging.DEBUG, f"===NODE===\n {node_text}")
            logging.log(logging.DEBUG, f"===EXTRA_INFO===\n {extra_info}")

            document = Document(text=node_text, extra_info=extra_info)
            documents.append(document)

        return documents
    
    def extract_documents_full(self) -> List[Document]:

        documents = self._extract_member_documents()

        documents.extend(self._extract_build_updates_documents())

        return documents
    
    @staticmethod
    def extract_metadata_build_update(record):
        field = record['fields']

        # METADATA
        # TODO Put the string and the names in lowercase all of them
        extra_info = {}
        extra_info['airtable_id'] = record['id']
        extra_info['member_name']=field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['member_name'], 'Unknown member name')
        project_name = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['build_project_name'], field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['project_name'], ''))
        extra_info['project_name']=project_name
        extra_info['slack_email']=field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['slack_email'], '')
        if field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['build_video_demo_available'], '') != '':
            extra_info['build_video_demo_available']=True
        build_update_date = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['build_update_date'], record.get('createdTime', ''))
        extra_info['build_update_date']=build_update_date
        extra_info['record_type']='build_updates'

        build_this_week = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["build_this_week"], '')
        build_url = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["build_url"], '')
        ask = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["ask_for_community"], '')
        milestone = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["milestone"], '')
        customer = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["how_close_to_first_paid_customer"], '')
        semantic_info = {
            'build_this_week': build_this_week,
            'build_url': build_url,
            'ask': ask,
            'milestone': milestone,
            'customer': customer
        }
        return extra_info, semantic_info
    
    def _extract_build_updates_documents(self):
        all_records = self.build_update_data

        documents = []
        for record in all_records:

            field = record['fields']
            logging.log(logging.DEBUG, f"===FIELD EXTRACTED FROM AIRTABLE===\n {field}")

            # # METADATA
            # extra_info = {}
            # extra_info['airtable_id'] = record['id']
            # extra_info['member_name']=field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['member_name'], 'Unknown member name')
            # project_name = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['build_project_name'], field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['project_name'], ''))
            # extra_info['project_name']=project_name
            # extra_info['slack_email']=field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['slack_email'], '')
            # if field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['build_video_demo_available'], '') != '':
            #     extra_info['build_video_demo_available']=True
            # build_update_date = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS['build_update_date'], record.get('createdTime', ''))
            # extra_info['build_update_date']=build_update_date
            # extra_info['record_type']='build_updates'

            # #TEXT FOR SEMANTIC SEARCH

            # build_this_week = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["build_this_week"], '')
            # build_url = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["build_url"], '')
            # ask = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["ask_for_community"], '')
            # milestone = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["milestone"], '')
            # customer = field.get(BUILD_UPDATES_AIRTABLE_COLUMNS["how_close_to_first_paid_customer"], '')

            extra_info, semantic_info = self.extract_metadata_build_update(record)
            build_this_week = semantic_info["build_this_week"]
            build_url = semantic_info["build_url"]
            ask = semantic_info["ask"]
            milestone = semantic_info["milestone"]
            customer = semantic_info["customer"]

            text = ''
            text+=f"Build Update for member {extra_info['member_name']}\n  "
            text+=f"Project name: {extra_info['project_name']}\n  "
            text+=f"Date of update: {extra_info['build_update_date'][:10]}\n\n  "
            text+=f'Built this week: {build_this_week}\n  '
            if build_url != '': 
                text+=f'Build url available here: {build_url}\n  '
            if milestone != '':
                text+=f'Milestone reached this week: {milestone}\n  '
            if customer != '':
                text+=f'Customers engagement: {customer}\n  '
            if ask!= '':
                text+=f'Ask for the community: {ask}\n  '

            logging.log(logging.DEBUG, f"===NODE===\n {text}")
            logging.log(logging.DEBUG, f"===EXTRA_INFO===\n {extra_info}")

            document = Document(text=text, extra_info=extra_info)
            documents.append(document)

        return documents


    def extract_nodes(self) -> List[BaseNode]:
        documents = self.extract_documents_full()

        nodes = [ TextNode(text=d.text, metadata=d.metadata) for d in documents]
        for node in nodes:
            record_id = node.metadata.get('airtable_id', '') #metadata['id'] should contain the id of the corresponding record in the airtable table
            if record_id != '':
                node.id_ = record_id
            node.metadata['extracted_timestamp']=time.time()
        return nodes


    def get_image_url_from_member_record(self, record) -> str:
        fields = record.get("fields", {})
        img_lst = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['profile_picture_url'], [])
        image_el = img_lst[0] if (img_lst and len(img_lst)>0) else {}
        image_url_thumbnails = image_el.get('thumbnails', {})
        image_url_large = image_url_thumbnails.get('large', {})
        image_url = image_url_large.get('url',"")
        logging.log(logging.DEBUG, f"Profile picture url: {image_url}")
        return image_url
    
    # def find_member_from_build_updates(self, member_name) -> str:
    #     table = self.api.table(self.base_id, self.member_table_id)
    #     from pyairtable.formulas import match
    #     formula = match({"Name": member_name})
    #     member_record = table.first(formula=formula)
    #     return member_record

    @staticmethod
    def find_member_by_name(member_name: str) -> List[dict]:
        engine = create_engine(DB_CONNECTION, pool_pre_ping=True)
        metadata = MetaData()
        build_club_members_table = Table(
            'build_club_members', 
            metadata, 
            autoload_with=engine
        )

        names = member_name.lower().split()
        search_name='%'
        for name in names:
            search_name+=f'{name}%'

        stmt = select(build_club_members_table.c.id, build_club_members_table.c.name, build_club_members_table.c.linkedin_url).where(func.lower(build_club_members_table.c.name).like(search_name))
        print("==stmt==:", stmt, '==search name==', search_name)

        with engine.connect() as connection:
            cursor_results = connection.execute(stmt)
            rows = cursor_results.fetchall()
            return rows
    
    def extract_rows(self) -> List[dict]:

        transformed = []
        all_records = self.member_data
        for record in all_records:
            fields = record.get("fields", {})
            transformed_detail = {}

            # download image TODO replace with get_image_url+from_member_record
            img_lst = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['profile_picture_url'], [])
            image_el = img_lst[0] if (img_lst and len(img_lst)>0) else {}
            image_url_thumbnails = image_el.get('thumbnails', {})
            image_url_large = image_url_thumbnails.get('large', {})
            image_url = image_url_large.get('url',"")
            logging.log(logging.DEBUG, f"Profile picture url: {image_url}")

            image=None
            if image_url != "":
                try:
                    image = download_image(image_url)
                except Exception as e:
                    logging.log(logging.INFO, f"Exception trying to download profile picture {image_url}: {e}")

            # Map fields to table
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

            #add image
            transformed_detail['profile_picture']=image

            transformed.append(transformed_detail)
        return transformed
    
    def extract_rows_for_dataframe(self) -> List[dict]:

        transformed = []
        all_records = self.member_data
        for record in all_records:
            fields = record.get("fields", {})
            transformed_detail = {}

            # download image
            img_lst = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS['profile_picture_url'], [])
            image_el = img_lst[0] if (img_lst and len(img_lst)>0) else {}
            image_url_thumbnails = image_el.get('thumbnails', {})
            image_url_large = image_url_thumbnails.get('large', {})
            image_url = image_url_large.get('url',"")
            logging.log(logging.DEBUG, f"Profile picture url: {image_url}")

            # Map fields to table
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
                elif key=="profile_picture_url":
                    transformed_detail["profile_picture_url"]=image_url
                else:
                    transformed_detail[key]=fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS[key], "")
                    if type(transformed_detail[key]) == list:
                        logging.log(logging.INFO, f'===FIELD IS A LIST=== {key}:{transformed_detail[key]} transforming to string')
                        transformed_detail[key] = str(transformed_detail[key])
            transformed_detail["id"]=record.get("id", str(uuid.uuid4()))

            logging.log(logging.INFO, f"==ROW==:\n{json.dumps(transformed_detail, indent=2)}")

            transformed.append(transformed_detail)
        return transformed
        
    def get_airtable_df(self, base_id: str, table_id: str)-> pd.DataFrame:

        # if (self.data is None): 
        #     _ = self._load_data()

        all_records = self.member_data

        # Extract the 'fields' content from each element
        fields = [item['fields'] for item in all_records]

        # Create a DataFrame from the extracted 'fields'
        df = pd.DataFrame(fields)

        return df
        
    def extract_skills(self) -> set:
        all_skills = set()
        for record in self.member_data:
            fields = record.get("fields", {})
            skills = fields.get(BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS["skills"], [])
            all_skills.update(skills)
        return all_skills
    
    def refresh_table(self):
        engine = create_engine(DB_CONNECTION)

        # Initialize metadata
        metadata = MetaData()

        # Reflect the table
        build_club_members = Table('build_club_members', metadata, autoload_with=engine)

        rows = self.extract_rows()

        for row in rows:
            stmt = insert(build_club_members).values(**row)
            with engine.begin() as connection:
                cursor = connection.execute(stmt)
        logging.log(logging.INFO, f'===YAY=== All rows inserted in build_club_members table')
#=========================================================================================================
# TODO IN PROGRESS


class AirTableDesigner():

    def _design_build_club_members_table(self, default_schema) -> Table:
        logging.log(logging.INFO, f'Design build_club_members table')
        metadata_obj = default_schema
        build_club_members = Table(
            "build_club_members",
            metadata_obj,
            Column("id", String(256), primary_key=True),
            Column("name", String(256)),
            Column("linkedin_url", String(512)),
            Column("skill_1", String(128)),
            Column("skill_2", String(128)),
            Column("skill_3", String(128)),
            Column("skill_4", String(128)),
            Column("based_in_sydney", String(256)),
            Column("member_location", String(256)),
            Column("member_acceptance_in_club", Boolean()),
            Column("ai_builder_linkedin_badge", String(256)),
            Column("referee", String(256)),
            Column("referrer_name", String(256)),
            Column("assignee", String(256)),
            Column("status", String(256)),
            Column("phone_number", String(256)),
            Column("are_you_building_in_squad", String(1024)),
            Column("best_time_for_build_sessions", String(1024)),
            Column("keen_for_ai_meetup", String(128)),
            Column("expectation_from_joining_club", String(4096)),
            Column("build_project", String(4096)),
            Column("past_work", String(4096)),
            Column("profile_picture", LargeBinary())
        )
        # metadata_obj.create_all(self.engine)
        return build_club_members
    
    def createTableBuildClubMemberIfNotExists(self):
        self.engine = create_engine(DB_CONNECTION)
        self.default_schema = MetaData()
        self._table = self._design_build_club_members_table(self.default_schema, "build_club_members")
        self.default_schema.create_all(self.engine)
"""Airtable reader."""
from typing import List

from llama_index.core.readers.base import BaseReader
from llama_index.core.schema import Document, BaseNode, TextNode
from pyairtable import Table, Api, Base
import pandas as pd
import json
import uuid

BUILD_CLUB_MEMBERS_AIRTABLE_COLUMNS = {
    "skills": "What are your areas of expertise you have (select max 4 please)",
    "name": "Name",
    "linkedin_url": "What's the link to your LinkedIn?",
    "build_project": "What will you build"
}


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
            print(extra_info)

            text_for_node = json.dumps(text_dict, indent=2)
            print(text_for_node)

            document = Document(text=text_for_node, extra_info=extra_info)
            documents.append(document)

        return documents

    def extract_nodes(self) -> List[BaseNode]:
        documents = self.extract_documents()

        nodes = [ TextNode(text=d.text, metadata=d.metadata) for d in documents]
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
        

    
    def get_airtable_df(self, base_id: str, table_id: str)-> pd.DataFrame:

        # if (self.data is None): 
        #     _ = self._load_data()

        all_records = self.data

        # Extract the 'fields' content from each element
        fields = [item['fields'] for item in all_records]

        # Create a DataFrame from the extracted 'fields'
        df = pd.DataFrame(fields)

        return df
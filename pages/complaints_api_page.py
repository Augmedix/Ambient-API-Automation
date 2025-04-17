import datetime
import json
import random
import uuid

import jwt
import pytest
from jwt import DecodeError

from pages.base_page import BasePage
from resources.data import Data
from utils.api_request_data_handler import APIRequestDataHandler
from utils.dbConfig import DB
from utils.helper import get_formatted_date_str
from utils.request_handler import RequestHandler


class ComplaintsApiPage(BasePage):
    def __init__(self, db_manager):
        self.db_manager = db_manager

    # Complaints
    note_builder_schema_name=pytest.configs.get_config("note_builder_schema_name")

    def get_first_complaints(self, complaint_type):
        query_data = self.db_manager.execute_query(f"SELECT id, name FROM  {self.note_builder_schema_name}.complaint where type='{complaint_type}' and is_published=1 order by rand() limit 1;")
        print(query_data)
        complaint_id = query_data['id']
        name = query_data['name']
        print(f'{complaint_type} COMPLAINT: Id={complaint_id}    name={name}')
        return complaint_id, name

    def get_complaint_element_variations_id_based_on_mobile_flag(self, complaints_id, mobile_flag=0):
        if mobile_flag == 0:
            query_data = self.db_manager.execute_query(
                f"SELECT id FROM {self.note_builder_schema_name}.element_variation where id in (SELECT element_variation_id FROM {self.note_builder_schema_name}.complaint_element_variation_mapping where complaint_id={complaints_id});", fetch_one=False )
        if mobile_flag == 1:
            query_data = self.db_manager.execute_query(f"SELECT id FROM {self.note_builder_schema_name}.element_variation where id in (SELECT element_variation_id FROM {self.note_builder_schema_name}.complaint_element_variation_mapping where complaint_id={complaints_id}  and display_on_mobile=1);", fetch_one=False)
        id_list = []
        for item in query_data:
            id_list.append(item['id'])
        print(f'{complaints_id}\'s MobileFlag={mobile_flag}, Element variations id : {id_list}')
        return id_list

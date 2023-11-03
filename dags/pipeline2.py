from airflow import DAG
from airflow.utils.dates import days_ago
from airflow.operators.python import PythonOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.bash import BashOperator
from airflow.models.param import Param
from airflow.models import Variable
from datetime import datetime, timedelta
import pandas as pd
import sys
import requests
import mysql.connector
import os
from airflow.models import Variable
from airflow.providers.google.cloud.operators.gcs import (
    GCSCreateBucketOperator,
    GCSDeleteBucketOperator,
    GCSDeleteObjectsOperator,
    GCSListObjectsOperator,
)

# To solve the stuck requests problem on MacOS while developing
try:
    from _scproxy import _get_proxy_settings
    _get_proxy_settings()
except:
    pass


"""
PINECONE CRUD FUNCTIONALITY
"""

import pandas as pd
import numpy as np
import os
import pinecone
import json
from ast import literal_eval
from typing import List, Iterator



EMBEDDING_MODEL = Variable.get("airflow_var_embedding_model")
PINECONE_ENVIRONMENT = Variable.get("airflow_var_pinecone_environment")
PINECONE_API_KEY = Variable.get("airflow_var_pinecone_api_key")
index_name = Variable.get("airflow_var_index_name")

PIPELINE_NAME='pipeline2'
BUCKET_NAME =  Variable.get("airflow_var_gcsbucket")


class BatchGenerator:
    def __init__(self, batch_size: int = 10) -> None:
        self.batch_size = batch_size
    
    # Makes chunks out of an input DataFrame
    def to_batches(self, df: pd.DataFrame) -> Iterator[pd.DataFrame]:
        splits = self.splits_num(df.shape[0])
        if splits <= 1:
            yield df
        else:
            for chunk in np.array_split(df, splits):
                yield chunk

    # Determines how many chunks DataFrame contains
    def splits_num(self, elements: int) -> int:
        return round(elements / self.batch_size)
    
    __call__ = to_batches

class pinecone_func():
    def __init__(self):
        self.EMBEDDING_MODEL = EMBEDDING_MODEL
        self.PINECONE_ENVIRONMENT = PINECONE_ENVIRONMENT
        self.PINECONE_API_KEY = PINECONE_API_KEY
        self.index_name = index_name
        pinecone.init(api_key=self.PINECONE_API_KEY,environment=self.PINECONE_ENVIRONMENT)
        self.curr_index = pinecone.Index(index_name=self.index_name)
        self.df_batcher = BatchGenerator(300)
        self.namespace = "sec-forms"

    def upsert(self,csv_filename):
        global pinecone
        article_df = pd.read_csv(csv_filename)
        article_df.columns=["text","tokenCount","title","vector_id","content_vector"]
        # article_df.columns=["title","text","tokenCount","content_vector"]
        article_df['vector_id'] = article_df.index
        article_df['content_vector'] = article_df.content_vector.apply(literal_eval)
        article_df['vector_id'] = article_df['title'] + "_" + article_df['vector_id'].apply(str)
        article_df['metadata'] = article_df.apply(lambda row: {"title": row['title'], "text": row['text']}, axis=1)
        dimension_len=len(article_df['content_vector'][0])

        if self.index_name not in pinecone.list_indexes():
            try:
                pinecone.create_index(name=self.index_name, dimension=dimension_len)
            except Exception as e:
                # Handle the exception here, you can log the error or take appropriate action.
                print(f"An error occurred: {str(e)}")

        print("Uploading vectors to content namespace..")
        for batch_df in self.df_batcher(article_df):
            try:
               response = self.curr_index.upsert(vectors=zip(batch_df.vector_id, batch_df.content_vector,batch_df.metadata))
            except Exception as e:
            # Handle the exception here, you can log the error or take appropriate action.
                print(f"An error occurred: {str(e)}")
        print(f"Upserted {response['upserted_count']} vectors in '{self.index_name}'")

    def delete_by_ids(self,vector_ids:list):
        try:
            response = self.curr_index.delete(ids=vector_ids)
            if response == {}:
                print(f"Deleted {len(vector_ids)} vector(s) from '{self.index_name}'")
        except Exception as e:
            error_data = json.loads(e.body)
            print(error_data['message'])
        
    def delete_by_form(self,form_titles:list):
        vector_ids = self.getIds(form_titles)
        self.delete_by_ids(vector_ids)

    def delete_all(self):
        global pinecone
        pinecone.delete_index(self.index_name)  
        print("Deleted all records")
        
    def stats(self):
        try:
            return self.curr_index.describe_index_stats()
        except Exception as e:
            print(e.body)

    def fetch_by_id(self,vector_ids:list):
        response = self.curr_index.fetch(vector_ids)
        print(response)

    def getIds(self,form_titles:list):
        response = self.stats()
        # print(response)
        total_count = response['total_vector_count']
        if total_count < 1:
            return []
        sample_vector = [0.1]* response['dimension']
        results = self.curr_index.query(vector=sample_vector, filter = {"title": {"$in":form_titles}}, top_k = total_count, include_metadata=True)
        vector_ids = []
        for vector in results['matches']:
            vector_ids.append(vector['id'])
        return vector_ids




"""
AIRFLOW DAG CODE
"""

def task_ValidateDAGConfig(**context):
    operationType = context["params"]["operationType"]
    operationPayload = context["params"]["operationPayload"]

    print("*** Input Config ***")
    print(operationType)
    print(operationPayload)
    print(type(operationPayload))

    if operationType == "upsert":
        if not isinstance(operationPayload, str):
            raise Exception("While upsert operation - link of csv file is expected as a string")
            
    elif operationType == "deleteByFormNames":
        if not isinstance(operationPayload, list):
            raise Exception("While deleteByFormNames operation - list of form names is expected")    
        if len(operationPayload)<1:
            raise Exception("While deleteByFormNames operation - You need to give atleast one form name in list")
        
        are_all_strings = all(isinstance(item, str) for item in operationPayload)
        if not are_all_strings:
            raise Exception("While deleteByFormNames operation - You need to give list of string values")
        
        contains_empty_strings = any(s == "" or s.isspace() for s in operationPayload)
        if contains_empty_strings:
            raise Exception("While deleteByFormNames operation - You need to give list of non-empty string values")

    elif operationType == "deleteByVectorIds":
        if not isinstance(operationPayload, list):
            raise Exception("While deleteByVectorIds operation - list of vector ids is expected")    
        if len(operationPayload)<1:
            raise Exception("While deleteByVectorIds operation - You need to give atleast one vector id in list")
        
        are_all_strings = all(isinstance(item, str) for item in operationPayload)
        if not are_all_strings:
            raise Exception("While deleteByVectorIds operation - You need to give list of string values")
        
        contains_empty_strings = any(s == "" or s.isspace() for s in operationPayload)
        if contains_empty_strings:
            raise Exception("While deleteByVectorIds operation - You need to give list of non-empty string values")

    elif operationType == "deleteAll":
        if operationPayload is not None:
            raise Exception("While deleteAll operation - Keep the operationPayload field empty/null")    
    pass

def task_ChooseOperationBranch(**context):
    
    if context['params']['operationType'] == "upsert":
        return "task_UpsertEmbeddingVectors"
    elif context['params']['operationType'] == "deleteByFormNames":
        return "task_DeleteEmbeddingVectorsByFormNames"
    elif context['params']['operationType'] == "deleteByVectorIds":
        return "task_DeleteEmbeddingVectorsByVectorIds"
    elif context['params']['operationType'] == "deleteAll":
        return "task_DeleteAllEmbeddingVectors"    
    

def task_UpsertEmbeddingVectors(**context):
    chunkEmbeddingCSVFileURL = context['params']['operationPayload']
    p = pinecone_func()
    p.upsert(chunkEmbeddingCSVFileURL)

def task_DeleteEmbeddingVectorsByFormNames(**context):
    listOfFormNamesToDelete = context['params']['operationPayload']
    p = pinecone_func()
    p.delete_by_form(listOfFormNamesToDelete)

def task_DeleteEmbeddingVectorsByVectorIds(**context):
    listOfVectorIdsToDelete = context['params']['operationPayload']
    p = pinecone_func()
    p.delete_by_ids(listOfVectorIdsToDelete)

def task_DeleteAllEmbeddingVectors(**context):
    p = pinecone_func()
    p.delete_all()

with DAG(
    dag_id=PIPELINE_NAME,
    description=PIPELINE_NAME,
    start_date=days_ago(1),
    schedule_interval=None,
    params={
    "operationType": Param("upsert", enum=["upsert", "deleteByFormNames", "deleteByVectorIds", "deleteAll"]),
    "operationPayload": Param("", type=["array", "string", "null"]),
    },
) as dag:


    task_ValidateDAGConfig = PythonOperator(
        task_id='task_ValidateDAGConfig',
        python_callable=task_ValidateDAGConfig
    )

    task_ChooseOperationBranch = BranchPythonOperator(
        task_id='task_ChooseOperationBranch',
        python_callable=task_ChooseOperationBranch
    )

    task_UpsertEmbeddingVectors = PythonOperator(
        task_id='task_UpsertEmbeddingVectors',
        python_callable=task_UpsertEmbeddingVectors
    )

    task_DeleteEmbeddingVectorsByFormNames = PythonOperator(
        task_id='task_DeleteEmbeddingVectorsByFormNames',
        python_callable=task_DeleteEmbeddingVectorsByFormNames
    )

    task_DeleteEmbeddingVectorsByVectorIds = PythonOperator(
        task_id='task_DeleteEmbeddingVectorsByVectorIds',
        python_callable=task_DeleteEmbeddingVectorsByVectorIds
    )

    task_DeleteAllEmbeddingVectors = PythonOperator(
        task_id='task_DeleteAllEmbeddingVectors',
        python_callable=task_DeleteAllEmbeddingVectors
    )

task_ValidateDAGConfig >> \
    task_ChooseOperationBranch >> \
        [
            task_UpsertEmbeddingVectors,
            task_DeleteEmbeddingVectorsByFormNames,
            task_DeleteEmbeddingVectorsByVectorIds,
            task_DeleteAllEmbeddingVectors
        ]
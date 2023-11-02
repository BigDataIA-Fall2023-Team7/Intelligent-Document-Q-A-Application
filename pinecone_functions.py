import pandas as pd
import numpy as np
import os
import pinecone
import json
from ast import literal_eval
from dotenv import load_dotenv
from typing import List, Iterator
load_dotenv()

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
        self.EMBEDDING_MODEL = "text-embedding-ada-002"
        self.PINECONE_ENVIRONMENT = os.getenv("PINECONE_ENVIRONMENT")
        self.PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
        self.index_name = os.getenv("INDEX_NAME")
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


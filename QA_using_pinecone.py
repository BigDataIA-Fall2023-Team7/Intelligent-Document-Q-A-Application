import openai

from typing import List, Iterator
import pandas as pd
import numpy as np
import os
import wget
import pinecone

from ast import literal_eval
from dotenv import load_dotenv
load_dotenv()

# Setting global variables
ENVIRONMENT = os.getenv("ENVIRONMENT")
API_KEY = os.getenv("PINECONE_API_KEY")
openai.api_key = os.getenv("OPEN_AI_KEY")
index_name = os.getenv("INDEX_NAME")

EMBEDDING_MODEL = "text-embedding-ada-002"
CHAT_COMPLETION_MODEL = "gpt-3.5-turbo"


#setting up pinecone database
pinecone.init(api_key=API_KEY,environment=ENVIRONMENT)

# Ignore unclosed SSL socket warnings - optional in case of these errors
import warnings
warnings.filterwarnings(action="ignore", message="unclosed", category=ResourceWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning) 

article_df = pd.read_csv('./combinedChunks.csv')

article_df.columns=["title","text","tokenCount","content_vector"]
article_df['vector_id'] = article_df.index
article_df['content_vector'] = article_df.content_vector.apply(literal_eval)
article_df['vector_id'] = article_df['vector_id'].apply(str)
article_df['metadata'] = article_df.apply(lambda row: {"title": row['title'], "text": row['text']}, axis=1)

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

df_batcher = BatchGenerator(300)
    
# Uncomment below code to delete and create a new index

# pinecone.create_index(name=index_name, dimension=len(article_df['content_vector'][0]))

index = pinecone.Index(index_name=index_name)

# Upsert content vectors in content namespace - this can take a few minutes
# def upsert_vectors():
print("Uploading vectors to content namespace..")
for batch_df in df_batcher(article_df):
    index.upsert(vectors=zip(batch_df.vector_id, batch_df.content_vector,batch_df.metadata))



'''The get_answer function is designed to retrieve answers to questions from a given set of form titles within a specified context.

Parameters:
# question: A string representing the question for which an answer is sought.
# form_titles: A array with form names that must be considered for the asnwer retrival
# top_k (optional): An integer specifying the maximum number of matches to retrieve. It defaults to 2.get_answer function '''

def get_answer(question, form_titles, top_k=2):

    # Create vector embeddings based on the title column
    ques_embedding = openai.Embedding.create(
                                            input=question,
                                            model=EMBEDDING_MODEL,
                                            )["data"][0]['embedding']

    # Query namespace passed as parameter using title vector
    response = index.query(vector = ques_embedding, 
                                    filter = {"title": {"$in":form_titles}},
                                    top_k=2,
                                    include_metadata=True,
                                    )
    context=''
    if response:
        for i in response['matches']:
            context += i['metadata']['text'] + "\n" 

    message = f'{context} \n\n Question: {question}'

    messages = [
        {"role": "system", "content": "You answer questions using the provided context only"},
        {"role": "user", "content": message},
    ]   

    print(message)

    response = openai.ChatCompletion.create(
        model=CHAT_COMPLETION_MODEL,
        messages=messages,
        temperature=0
    )
    response_message = response["choices"][0]["message"]["content"]
    return response_message                             


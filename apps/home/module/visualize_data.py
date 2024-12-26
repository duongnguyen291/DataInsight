import pandas as pd
from .generate_code import generate_code_visualize_data
from dotenv import load_dotenv
import os
import time
import matplotlib.pyplot as plt
import boto3
import plotly.express as px
load_dotenv()
minio_url = os.getenv('MINIOURL')
minio_access_key = os.getenv('MINIO_ACESS_KEY')
minio_secret_key = os.getenv('MINIO_SECRET_KEY')
s3 = boto3.client(
    's3',
    endpoint_url=minio_url,
    aws_access_key_id=minio_access_key,
    aws_secret_access_key=minio_secret_key
)
class VisualizeData:
    def __init__(self,df):
        self.df=df
    @classmethod
    #Load file for visualization
    def load_data(cls,file_path):
        if(file_path.endswith("csv")):
            df=pd.read_csv(file_path)
        else:
            df=pd.read_excel(file_path)
        return cls(df)
    def visualize_data_df(self,metadata,prompt):
        code=generate_code_visualize_data(metadata,prompt)
        print("Using:")
        print(code)
        local_context={}
        exec(code,globals(),local_context)
        if('visualize') in local_context:
            return local_context['visualize'](self.df)
import pandas as pd
from .generate_code import generate_code_visualize_data
import os
import time
import matplotlib.pyplot as plt
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
    def visualize_data_df(self,metadata):
        code=generate_code_visualize_data(metadata)
        print("Using:")
        print(code)
        local_context={}
        exec(code,globals(),local_context)
        if('visualize') in local_context:
            return local_context['visualize'](self.df)
import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
from pathlib import Path
import json
import psycopg2
from sentence_transformers import SentenceTransformer
import requests
from .query import query_most_similar
# embedding model
model = SentenceTransformer("C:\\Users\\Lenovo\\.cache\huggingface\hub\\bge\models--BAAI--bge-m3\snapshots\\5617a9f61b028005a4858fdac845db406aefb181")

def get_embedding(text):
    return model.encode(text)

# Connect to the database
conn = psycopg2.connect(
    dbname="rag_db",
    user="admin",
    password="admin",
    host="localhost",
    port=5435
)
cursor = conn.cursor()
print("Connected to the database.")


# Load API key từ file .env
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
)

def get_chart_desc(plotjson, title):
    """
    Phân tích hình ảnh sử dụng OpenAI Vision API
    
    Args:
        plotjson: Json data của plot
        api_key (str): OpenAI API key
    
    Returns:
        str: Mô tả về plot
    """
    prompt = f"""
    ###Instruct###:
    You are an expert in data visualization. Your task is to extract and summarize pure factual information directly from a chart related to import-export activities. The summary should accurately describe all visible trends, patterns, relationships, and data points without adding any interpretations, insights, or reasoning.

    **Requirements**:
    *Content*:
    - Include all observable information, such as:
        - Chart title.
        - Axis labels and their units.
        - Data points, values, percentages, and categories.
        - Trends, patterns, and relationships explicitly visible in the chart.
        - Legends, annotations, or any highlighted details.
    *Exclusions*:
        - Do not include any insights, analysis, or reasoning beyond the chart's explicit content.
        - Avoid hypothetical scenarios, future projections, or context not visible in the chart.
        - Do not provide vague or generic descriptions such as "This is a line chart."
    
    **Special Instructions**:
    - Write the summary as a coherent passage, ensuring it is concise, factual, and comprehensive.
    - Include all relevant details in a neutral tone, accurately reflecting what is shown in the chart.
    - Avoid undesired output examples like:
        - "The chart suggests..." (Adds reasoning or inference).
        - "This data might indicate..." (Speculative or hypothetical statements).
    
    **Desired Example**:
    "The chart titled 'Export Volume by Category (2022)' shows the distribution of export volumes across three categories: electronics (35%), textiles (20%), and agricultural products (15%). A line graph plots monthly export volumes from January to December 2022, with a noticeable peak in August and a decline in February. The x-axis represents months, and the y-axis measures export volume in billions of USD. An annotation highlights that August's peak was due to a seasonal increase in agricultural exports."

    **Undesired Examples**:
    - "The chart shows an interesting trend in exports." (Vague and lacks detail).
    - "The data implies electronics are the most important export category." (Includes reasoning not in the chart).
    
    ###BEGIN_TASK###
    Summarize the factual information presented in the chart into a clear and concise passage. Follow all the requirements, guidelines, and special instructions provided.
    Title: {title}
    Plot Data (JSON): {json.dumps(plotjson, indent=2)}
    Generated Summary:

    ###END_TASK###
    """
    # Prepare messages for API
    messages = [
        {
            "role": "user",
            "content": prompt

        }
    ]
    
    # Call the API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content.replace("*","").replace("#","")



# def analyze_image(plotjson, desc):
#     """
#     Phân tích hình ảnh sử dụng OpenAI Vision API
    
#     Args:
#         plotjson: Json data của plot
#         api_key (str): OpenAI API key
    
#     Returns:
#         str: Mô tả về plot
#     """
#     # Prepare messages for API
#     messages = [
#         {
#             "role": "user",
#             "content": f"""
#             Analyze the following data visualization and provide insights:
#             Description: {desc}
#             Plot Data (JSON): {json.dumps(plotjson, indent=2)}
#             Provide insights on trends, relationships, and any unusual observations that might benefit a business.
#             """
#         }
#     ]
    
#     # Call the API
#     response = client.chat.completions.create(
#         model="gpt-4o-mini",
#         messages=messages,
#     )
#     return response.choices[0].message.content.replace("*","").replace("#","")

def parse_context(context):
    final = ''
    for i, res in enumerate(context):
        c = f'{i+1}. {res[0]}'
        final += c
        final += '\n'
        final += '  '
    return final

def get_insight(plotjson,title):
    try:
        description=get_chart_desc(plotjson,title)
        all_cont = []
        for i in range(1,6):
            context=query_most_similar(description, table_name="test", top_k=2)
            context=parse_context(context)
            all_cont.append(context)
        context_print = f"""
        *Context*: 

        1. Foundational Information on Import-Export:
            {all_cont[0]}

        2. Historical Data and Trends:
            {all_cont[1]}
            
        3. Detailed Contextual Information:
            {all_cont[2]}
        
        4. Expert Analyses and Reports:
            {all_cont[3]}
            
        5. Correlations and Comparisons:
            {all_cont[4]}
        """
        get_insight_prompt = f"""
        ###Instruct###:
        You are an expert in data analysis and strategy development. Your task is to generate specific, actionable, and impactful insights from the provided data. The input consists of the chart title, a description summarizing the chart's key features, the chart itself, and relevant retrieved context. Use all available information to produce well-supported insights that directly address observed data and trends, avoiding mere restatements of the description.

        **Requirements**:
        *Content*:
        - Analyze the chart and its description, combining observations with retrieved context.
        - Generate insights that are:
            - Specific: Clearly identify opportunities, risks, or patterns supported by the data and context.
            - Actionable: Provide realistic recommendations or implications that drive decision-making.
            - Impactful: Focus on observations with significant relevance to the domain.
        - Each insight must add value by integrating data and context, rather than summarizing the chart description.
        *Exclusions*:
        - Do not restate or paraphrase the chart description without adding new analysis or actionable recommendations.
        - Avoid vague, generalized, or unsupported statements such as "exports are increasing."
        - Do not include hypothetical assumptions not backed by the data or context.

        **Special Instructions**:
        - Reference specific patterns, relationships, or anomalies in the chart while leveraging the retrieved context for a comprehensive perspective.
        - Ensure all insights are clear, actionable, and aligned with the domain.
        - Avoid redundancy and focus on providing distinct, meaningful insights.

        ###Input###:
        Title: {title}
        Chart Description: {description}
        Chart: {plotjson}
        *Context*: 
        Foundational Information on Import-Export:
            {all_cont[0]}
        Historical Data and Trends:
            {all_cont[1]}
        Detailed Contextual Information:
            {all_cont[2]}
        Expert Analyses and Reports:
            {all_cont[3]}
        Correlations and Comparisons:
            {all_cont[4]}
        ###BEGIN_TASK###
        Analyze the input and generate 3-5 specific, actionable, and impactful insights based on the chart, its description, and the retrieved context. Ensure that all insights are supported by the data and context without repeating the chart description.
        Based on those insights, construct a step by step, specific, feasible, impactful action plan to improve business, especially make more profit.
        1.
        2.
        3.
        4.
        5.
        ###END_TASK###
        """
        messages = [
        {
            "role": "user",
            "content": get_insight_prompt
        }
    ]
        # Call the API
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
        )
        final = response.choices[0].message.content.replace("*","").replace("#","")
        print(context_print)
        print("Chart insights:")
        print(final)
        return context_print, final
    except Exception as e:
        print(f"Có lỗi xảy ra {str(e)}")
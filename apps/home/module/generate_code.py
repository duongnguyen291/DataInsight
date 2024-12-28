import os
import environ
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
# Load API key từ file .env
load_dotenv(".env", override=True)
print(os.environ.get("API_KEY"))
client = OpenAI(
    api_key=os.environ.get("API_KEY")
)
print(os.environ.get("API_KEY"))
NGROK_URL=os.environ.get("NGROK_URL")
print(NGROK_URL)

def generate_code_process_data(metadatas):
    """
    Gọi OpenAI API để sinh mã code xử lý dữ liệu dựa trên metadata.
    """
    # Tạo prompt mô tả yêu cầu xử lý dữ liệu dựa trên metadata
    prompt = f"""
    Given the following metadatas, generate Python code to take in multiple dataframes that might have correlation to each other and combine them into one. If there's only one metadata then just clean up that dataframe
    Metadatas: {metadatas}
    ONLY PROVIDE THE PYTHON CODE, START WITH def process(df):.ABSOLUTELY DO NOT include python at the start and DO NOT import anything.
    The generated code must only include a function named `process(df)` that takes an array of DataFrames as input and returns the processed DataFrame. Ensure that the code is formatted correctly and performs appropriate data cleaning, transformations, or aggregations based on the metadatas provided.
    """

    try:
        # Gọi OpenAI API để sinh mã code
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Lấy mã code từ phản hồi của API
        code =  response.choices[0].message.content.strip()
        print("Before:")
        print(code)
        if code.lower().startswith("python"):
            code = "\n".join(code.splitlines()[1:]).strip()
        print("After:")
        print(code)
        return code
    except Exception as e:
        print(f"Error generating code: {e}")
        return """
def process(df):
    # Default processing: remove rows with NaN values
    df.dropna(inplace=True)
    return df
"""
#Generate code for visualizing data
def generate_code_visualize_data(metadata,needs):
    prompt=f"""
    Given the following metadata, generate Python code to visualize a pandas DataFrame with appropriate graph and must follow the user's needs (if exist) using plotly.
    Metadata: {metadata}
    Needs:{needs}
    ONLY PROVIDE PYTHON CODE, START WITH def visualize(df): . ABSOLUTELY DO NOT include python at the start, and DO NOT import anything.
    The generated code must only include a function named visualize(df) that takes a DataFrame as input, creates multiple interactive plots using plotly that can help the user gain insights based on their needs, and returns an array of dictionaries with 2 keys: 'plot' and 'description'. The 'plot' should be a plot created using plotly, and use update_layout to set the height to 600, and 'description' should provide insights about the plot. Ensure the plots are relevant to the metadata and user needs.
    """
    try:
        # Gọi OpenAI API để sinh mã code
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )

        # Lấy mã code từ phản hồi của API 
        code =  response.choices[0].message.content.strip()
        print("Before visualize:")
        print(code)
        if code.lower().startswith("python"):
            code = "\n".join(code.splitlines()[1:]).strip()
        print("After visualize:")
        print(code)
        return code
    except Exception as e:
        print(f"Error generating code: {e}")


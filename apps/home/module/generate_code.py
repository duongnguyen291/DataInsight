import os
import environ
from dotenv import load_dotenv
from openai import OpenAI
# Load API key từ file .env
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
)

def generate_code_process_data(metadata):
    """
    Gọi OpenAI API để sinh mã code xử lý dữ liệu dựa trên metadata.
    """
    # Tạo prompt mô tả yêu cầu xử lý dữ liệu dựa trên metadata
    prompt = f"""
    Given the following metadata, generate Python code to process a pandas DataFrame.
    Metadata: {metadata}
    ONLY PROVIDE THE PYTHON CODE, START WITH import pandas as pd.
    The generated code must include a function named `process(df)` that takes a DataFrame as input and returns the processed DataFrame. Ensure that the code is formatted correctly and performs appropriate data cleaning, transformations, or aggregations based on the metadata provided.
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
        if code.lower().startsWith("python"):
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


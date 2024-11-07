import os
import environ
from dotenv import load_dotenv
from openai import OpenAI
import matplotlib.pyplot as plt
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
    ONLY PROVIDE THE PYTHON CODE, START WITH def process(df):.ABSOLUTELY DO NOT include python at the start and DO NOT import anything.
    The generated code must only include a function named `process(df)` that takes a DataFrame as input and returns the processed DataFrame. Ensure that the code is formatted correctly and performs appropriate data cleaning, transformations, or aggregations based on the metadata provided.
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
def generate_code_visualize_data(metadata):
    prompt=f"""
    Given the following metadata, generate Python code to visualize a pandas DataFrame with an appropriate type of graph using matplotlib.pyplot.
    Metadata: {metadata}
    ONLY PROVIDE PYTHON CODE, START WITH def visualize(df): .ABSOLUTELY DO NOT include python at the start, and DO NOT import anything.
    The generated code must only include a function named visualize(df) that takes a DataFrame as input, creates a suitable plot, and must saves it as an image file in a folder named 'plotImages' inside /apps/static/assets/img, the function should return the name of the image. The filename should be unique for each plot. Ensure that the code is formatted correctly."""
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


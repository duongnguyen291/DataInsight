import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
from pathlib import Path
# Load API key từ file .env
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
)

def encode_image(image_path):
    """
    Mã hóa hình ảnh thành base64 string
    """
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def analyze_image(image_path, image_desc):
    """
    Phân tích hình ảnh sử dụng OpenAI Vision API
    
    Args:
        image_path (str): Đường dẫn đến file hình ảnh
        api_key (str): OpenAI API key
    
    Returns:
        str: Mô tả về hình ảnh
    """
    # Mã hóa hình ảnh
    base64_image = encode_image(image_path)
    # Prepare messages for API
    messages = [
        {
            "role": "user",
            "content":[{
                "type":"text",
                "text":f"Give comments and analysis of the data of the graph with this context: {image_desc}",
            },
            {
                "type":"image_url",
                "image_url":{
                    "url":f"data:image/jpeg;base64,{base64_image}"
                }
            }]
        }
    ]
    
    # Call the API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content
def get_insight(image_path,image_desc):
    try:
        description=analyze_image(image_path,image_desc)
        print("Image description:")
        print(description)
        return description
    except Exception as e:
        print(f"Có lỗi xảy ra {str(e)}")
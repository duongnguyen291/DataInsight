import os
from dotenv import load_dotenv
from openai import OpenAI
import base64
from pathlib import Path
import json
# Load API key từ file .env
load_dotenv()
client = OpenAI(
    api_key=os.environ.get("API_KEY"),
)

def analyze_image(plotjson, desc):
    """
    Phân tích hình ảnh sử dụng OpenAI Vision API
    
    Args:
        plotjson: Json data của plot
        api_key (str): OpenAI API key
    
    Returns:
        str: Mô tả về plot
    """
    # Prepare messages for API
    messages = [
        {
            "role": "user",
            "content": f"""
            Analyze the following data visualization and provide insights:
            Description: {desc}
            Plot Data (JSON): {json.dumps(plotjson, indent=2)}
            Provide insights on trends, relationships, and any unusual observations that might benefit a business.
            """
        }
    ]
    
    # Call the API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
    )
    return response.choices[0].message.content.replace("*","").replace("#","")
def get_insight(plotjson,desc):
    try:
        description=analyze_image(plotjson,desc)
        print("Image description:")
        print(description)
        return description
    except Exception as e:
        print(f"Có lỗi xảy ra {str(e)}")
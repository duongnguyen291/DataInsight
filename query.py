import psycopg2
from sentence_transformers import SentenceTransformer
import requests

model = SentenceTransformer("BAAI/bge-m3")

def get_embedding(text):
    return model.encode(text)

# Connect to the database
conn = psycopg2.connect(
    dbname="rag_db10",
    user="admin",
    password="admin",
    host="localhost",
    port=5435
)
cursor = conn.cursor()
print("Connected to the database.")
def query_most_similar(input_text, table_name='fiction', top_k=5):
    embedding = get_embedding(input_text).tolist()  # Get embedding for the input text
    with conn.cursor() as cur:
        cur.execute(f"""
        WITH RankedResults AS (
            SELECT DISTINCT ON (info)
                info,
                insight,
                embedding <-> %s::VECTOR AS vector_similarity,
                1.0 - (ts_rank(to_tsvector('english', info), plainto_tsquery('english', %s)) / 
                    (SELECT MAX(ts_rank(to_tsvector('english', info), plainto_tsquery('english', %s))) FROM {table_name})
                ) AS normalized_text_distance
            FROM {table_name}
        )
        SELECT info, insight,
            (0.7 * vector_similarity + 0.3 * normalized_text_distance) as hybrid_score
        FROM RankedResults
        ORDER BY hybrid_score ASC
        LIMIT %s
        """, (embedding, input_text, input_text, top_k))
        results = cur.fetchall()
    return results

print("Enter your query: ")
input_text = input()
results = query_most_similar(input_text, table_name='fiction', top_k=5)
print("Retrived documents")
# print(results)
# for result in results:
#     print(f"Title: {result[0]}, Similarity: {result[1]}")

def context(results=results):
    context = ''
    for i, result in enumerate(results):
        c = f"{i+1}. Information: {result[0]}"
        context += c
        context += "\n"
    return context

def pairs(results=results):
    pairs = ''
    for i, result in enumerate(results):
        c = f"{i+1}. Information: {result[0]} \n   Insights: {result[1]}"
        pairs += c
        pairs += "\n"
    return pairs

# print(context(results))
# print(pairs(results))

prompt = f""" 
###Instruction###:
You are an expert assistant in manufacturing operations. Your task is to generate actionable insights for a given input based on the retrieved manufacturing-related data. The retrieved data consists of pairs of Information and Actionable Insights that provide context and examples to guide your reasoning.

###Context###:
The following retrieved information provides relevant context extracted from the manufacturing-related database:
{context(results)}
###Examples###:
Here are pairs of retrieved Information and their corresponding Actionable Insights to serve as examples:
{pairs(results)}
###Task###:
Given the following input information:

**Input Information**: {input_text}
Use the provided context and examples to generate actionable insights specifically for the input information. Ensure the insights are practical, concise, and aligned with the manufacturing domain.

**Output Format**:

Input Information: {input_text}
Generated Actionable Insights: [Your insights here]
"""


url = "https://01e7-34-80-1-243.ngrok-free.app/predict"
payload = {"input_text": prompt}
response = requests.post(url, json=payload)
print('Response: \n')
print(response.json())


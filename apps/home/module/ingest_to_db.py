import psycopg2
import pandas as pd
import json
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("C:\\Users\\Lenovo\\.cache\huggingface\hub\\bge\models--BAAI--bge-m3\snapshots\\5617a9f61b028005a4858fdac845db406aefb181")

def get_embedding(text):
    return model.encode(text)

conn = psycopg2.connect(
    dbname="rag_db",
    user="admin",
    password="admin",
    host="localhost",
    port=5435
)
cursor = conn.cursor()
print("Connected to the database.")
# cursor.execute("""
#     SELECT table_name
#     FROM information_schema.tables
#     WHERE table_schema = 'public';
# """)

# # Fetch all table names
# tables = cursor.fetchall()

# # Print table names
# print("Tables in the database:")
# for table in tables:
#     print(table[0])
df = pd.read_json(f"data\generated_data_1000_prompt1_cleaned.jsonl", lines=True)
for row in df.itertuples():
    print(row[1])
    break

for i in range(1,6):
    df = pd.read_json(f"data\generated_data_1000_prompt{i}_cleaned.jsonl", lines=True)
    # print(df.head())
    count = 0
    error_count=0
    for row in df.itertuples():
        try:
            print(f"Process item {count+1} ...")
            info = row[1]
            embedding = get_embedding(info)
            cursor.execute(f"INSERT INTO p{i} (info, embedding) VALUES (%s, %s)", (info, embedding.tolist()))
            print(f"Process item {count+1} done.")
        except Exception as e:
            print(f"Error processing item {count+1}: {e}")
            error_count+=1
        count+=1
    print(f"Total error: {error_count} in prompt{i}")
    print(f"Total item: {count} in prompt{i}")
conn.commit()
cursor.close()
conn.close()

print("Data ingested successfully.")
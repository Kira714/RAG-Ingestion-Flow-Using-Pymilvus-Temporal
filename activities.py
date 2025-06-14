import aiohttp
import os
import uuid
import tempfile
import cohere
from typing import List, Dict
from unstructured.partition.pdf import partition_pdf
from pymilvus import connections, Collection, utility, DataType, CollectionSchema, FieldSchema,Milvus
from temporalio import activity
from dotenv import load_dotenv
load_dotenv()

# === Setup ===
TEMP_DIR = tempfile.gettempdir()
CO_API_KEY = os.getenv("CO_API_KEY")
if not CO_API_KEY:
    raise EnvironmentError("❌ COHERE_API_KEY not set in environment variables")

co = cohere.Client(CO_API_KEY)
connections.connect("default", host="localhost", port="19530")
collection_name = "doc_chunks"

# Adjust the dimension based on the Cohere model you're using
# Common Cohere models:
# - embed-english-v3.0 -> 4096
# - embed-english-light-v3.0 -> 1024
# === Milvus Setup ===

# embedding_dim = 4096  # Replace with 768 or 1024 if you're using smaller models

if not utility.has_collection(collection_name):
    fields = [
        FieldSchema(name="chunk_id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=4096),  # ✅ Correct dimension
    ]
    schema = CollectionSchema(fields, description="Document chunks with embeddings")
    Collection(name=collection_name, schema=schema)
    print(f"Collection '{collection_name}' created with dim=4096.")
else:
    print(f"Collection '{collection_name}' already exists.")

collection = Collection(name=collection_name)
print(f"Type of collection: {type(collection)}")
collection.load()  # Important: Load collection before inserting/searching

# === Activities ===

@activity.defn
async def fetch_document(file_url: str, file_id: str) -> str:
    try:
        filename = f"{file_id}_{uuid.uuid4().hex[:6]}.pdf"
        filepath = os.path.join(TEMP_DIR, filename)

        async with aiohttp.ClientSession() as session:
            async with session.get(file_url) as resp:
                if resp.status != 200:
                    raise Exception(f"Failed to download file: {resp.status}")
                with open(filepath, "wb") as f:
                    f.write(await resp.read())

        return filepath
    except aiohttp.ClientError as e:
        raise Exception(f"Network error: {str(e)}")
    except Exception as e:
        raise Exception(f"Download failed: {str(e)}")

@activity.defn
def parse_document(filepath: str) -> List[str]:
    try:
        elements = partition_pdf(filename=filepath)
        return [el.text.strip() for el in elements if el.text and el.text.strip()]
    except Exception as e:
        raise Exception(f"Parsing failed: {str(e)}")

@activity.defn
def generate_embeddings(chunks: List[str]) -> List[List[float]]:
    vectors = []
    try:
        if not chunks:
            return []
        print(f"📥 Generating embeddings for {len(chunks)} chunks...")
        response = co.embed(texts=chunks, model="embed-english-v2.0")
        vectors = response.embeddings
    except Exception as e:
        print(f"❌ Error while generating embeddings: {str(e)}")
    return vectors

@activity.defn
def store_in_milvus(vectors: List[List[float]]) -> Dict:
    try:
        if not vectors:
            raise ValueError("No vectors to insert into Milvus")

        data_to_insert = [vectors]
        collection.insert(data_to_insert)
        milvus = Milvus(host="localhost", port="19530")
        milvus.flush([collection_name])


        return {"inserted": len(vectors)}
    except Exception as e:
        raise Exception(f"Milvus insert error: {str(e)}")

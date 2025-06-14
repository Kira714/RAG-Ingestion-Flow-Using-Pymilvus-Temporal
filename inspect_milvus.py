from pymilvus import connections, Collection

# Connect to Milvus
connections.connect("default", host="localhost", port="19530")

# Load the collection
collection = Collection("doc_chunks")
collection.load()

# Show basic collection info
print("✅ Connected to Collection:", collection.name)
print("\n📄 Schema:")
print(collection.schema)

# Number of vectors inserted
print("\n📊 Total entities in collection:", collection.num_entities)

# Optional: Fetch sample records
print("\n🔍 Sample inserted data:")
try:
    results = collection.query(
        expr="chunk_id >= 0",
        output_fields=["chunk_id"],
        limit=2
    )
    for r in results:
        print(r)
except Exception as e:
    print("⚠️ Query failed:", e)

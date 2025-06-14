
# 📄 RAG Document Ingestion Pipeline using Temporal & Milvus

This project implements a distributed, asynchronous document ingestion pipeline using **Temporal.io**, **Milvus 2.0.2**, **Cohere embeddings**, and **Python 3.9.13**. It fetches a document from a given URL, parses and chunks the content, generates vector embeddings, and stores the results into Milvus — all orchestrated through a Temporal Workflow.

---

## 🚀 Features

- Temporal Workflow that handles document ingestion end-to-end
- Activities for:
  - Downloading PDFs
  - Parsing PDFs into chunks using `unstructured`
  - Generating embeddings using **Cohere API**
  - Inserting data into **Milvus 2.0.2** vector database
- Asynchronous activity execution using `asyncio` and `ThreadPoolExecutor`
- Retry policies and robust error handling
- Environment-safe secrets loading via `.env`

---

## 📂 Folder Structure

```
.
├── activities.py         # Temporal activities
├── client.py             # Triggers the workflow with sample input
├── workflows.py          # Workflow orchestration logic
├── worker.py             # Temporal Worker definition
├── drop_collection.py    # Utility to drop Milvus collection
├── requirements.txt      # Python package dependencies
├── .env                  # Environment variables (not committed)
├── .gitignore
├── docker-compose.yml    # Temporal + Milvus setup
└── Dockerfile            # (Optional container build)
```

---

## ⚙️ Setup Instructions

### 1. Clone the Repo

```bash
git clone https://github.com/Kira714/RAG-Ingestion-Flow-Using-Pymilvus-Temporal.git
cd RAG-Ingestion-Flow-Using-Pymilvus-Temporal
```

### 2. Environment Setup

Create a virtual environment and install dependencies:

```bash
python3.9 -m venv venv
source venv/bin/activate   # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

## 📦 Dependencies and Versions

Below are the main packages and their versions used in this project:

| Package        | Version   |
|----------------|-----------|
| Python         | 3.9.13    |
| pymilvus       | 2.0.2     |
| temporalio     | latest    |
| cohere         | latest    |
| grpcio         | ≥1.57.0   |
| protobuf       | 3.20.3    |
| unstructured   | latest    |
| python-dotenv  | latest    |
| aiohttp        | latest    |

### 3. Add `.env` File

Create a `.env` file:

```
CO_API_KEY=your_cohere_api_key_here
```

---

## 🐳 Temporal & Milvus Setup (Docker)

Ensure Docker is installed, then run:

```bash
docker-compose up -d
```

This will start:
- Temporal server on port `7233`
- Milvus server on port `19530`

---

## ▶️ Running the Pipeline

### 1. Start the Temporal Worker

```bash
python worker.py
```

### 2. Trigger the Workflow

In a separate terminal:

```bash
python client.py
```

This will:
- Download a sample PDF
- Parse it into chunks
- Generate embeddings via Cohere
- Insert the embeddings into Milvus

---

## 🧠 Design Explanation

### Workflow & Activities

- **Workflow:** Orchestrates all 4 stages: fetch, parse, embed, store.
- **Activities:**
  - `fetch_document`: Downloads file using `aiohttp`
  - `parse_document`: Uses `unstructured.partition.pdf` to chunk
  - `generate_embeddings`: Uses `cohere` client
  - `store_in_milvus`: Inserts embeddings into Milvus with schema:  
    ```python
    chunk_id (INT64, primary, auto_id=True)
    embedding (FLOAT_VECTOR, dim=4096)
    ```

### Concurrency & AsyncIO

- Used `ThreadPoolExecutor` inside the Temporal Worker
- Non-blocking download via `aiohttp`
- Activities run efficiently without blocking event loop

### Error Handling

- Activities wrapped in `try-except` blocks
- RetryPolicy on all activity calls:
  - Initial delay: 5s
  - Max attempts: 5
  - Backoff: 2x

### Assumptions

- Input files are valid PDFs accessible via public URLs
- Cohere key and Milvus services are available locally

---

## ✅ Evidence of Success

### Temporal Workflow UI

Once executed, visit [http://localhost:8233](http://localhost:8233) and view:
- Workflow status: `COMPLETED`
- Output: Sample embeddings + metadata

### Terminal Logs

```
Collection 'doc_chunks' already exists.
📥 Generating embeddings for 18 chunks...
Workflow result:
{'file_id': 'file_lime_001', 'num_chunks': 18, 'sample': [[...], [...]]}
```

---

## 🧪 Example Input

Inside `client.py`:

```python
file_id = "file_lime_001"
file_url = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
```

You can change this to any valid public PDF URL.

---


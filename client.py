import asyncio
import uuid
from temporalio.client import Client
from workflows import DocumentIngestionWorkflow

async def main():
    for i in range(5):
        try:
            client = await Client.connect("localhost:7233")
            break
        except Exception as e:
            print(f"Retrying Temporal connection in 3s... ({i+1}/5): {e}")
            await asyncio.sleep(3)
    else:
        raise RuntimeError("Failed to connect to Temporal after retries")

    file_id = "file_lime_001"
    file_url = "https://ontheline.trincoll.edu/images/bookdown/sample-local-pdf.pdf"
    workflow_id = f"workflow-{file_id}-{uuid.uuid4().hex[:6]}"

    result = await client.start_workflow(
        workflow=DocumentIngestionWorkflow.run,
        args=[file_id, file_url],
        id=workflow_id,
        task_queue="doc-ingest-queue"
    )

    print("Workflow result:")
    print(await result.result())

if __name__ == "__main__":
    asyncio.run(main())
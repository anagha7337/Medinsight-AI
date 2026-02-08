from src.helper import load_pdf_file, text_split, download_hugging_face_embeddings

from pinecone import Pinecone, ServerlessSpec
from langchain_pinecone import PineconeVectorStore

from dotenv import load_dotenv
import os
import time

load_dotenv()

PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

# Load data
print("Loading PDFs...")
extracted_data = load_pdf_file(data="Data/")

print("Splitting text...")
text_chunks = text_split(extracted_data)

print("Total chunks:", len(text_chunks))

# Load embeddings
print("Loading embeddings...")
embeddings = download_hugging_face_embeddings()

# Connect Pinecone
pc = Pinecone(api_key=PINECONE_API_KEY)
index_name = "medicalbot"

# Create index if not exists
existing_indexes = [i.name for i in pc.list_indexes()]

if index_name not in existing_indexes:
    print("Creating index...")
    pc.create_index(
        name=index_name,
        dimension=384,
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",
            region="us-east-1"
        )
    )
    time.sleep(10)  # wait for creation

# Upload documents to Pinecone
print("Uploading embeddings to Pinecone...")

docsearch = PineconeVectorStore.from_documents(
    documents=text_chunks,
    embedding=embeddings,
    index_name=index_name
)

print("Indexing complete.")

from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os
import requests

# Extract data from PDF File
def load_pdf_file(data):
    loader = DirectoryLoader(data,
                             glob="*.pdf",
                             loader_cls=PyPDFLoader)
    documents = loader.load()
    return documents

# Split data into text chunks
def text_split(extracted_data):
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=20)
    text_chunks = text_splitter.split_documents(extracted_data)
    return text_chunks

# Embeddings using HuggingFace new router API
def download_hugging_face_embeddings():

    class FixedHFEmbeddings:
        def __init__(self):
            self.model = "sentence-transformers/all-MiniLM-L6-v2"
            self.token = os.getenv("HUGGINGFACEHUB_API_TOKEN")

        def _get_vector(self, text):
            response = requests.post(
                f"https://router.huggingface.co/hf-inference/models/{self.model}/pipeline/feature-extraction",
                headers={"Authorization": f"Bearer {self.token}"},
                json={"inputs": text}
            )
            print(f"HF Status: {response.status_code}")
            result = response.json()
            if isinstance(result[0], list):
                return result[0]
            return result

        def embed_documents(self, texts):
            return [self._get_vector(text) for text in texts]

        def embed_query(self, text):
            return self._get_vector(text)

        def __call__(self, text):
            return self._get_vector(text)

    return FixedHFEmbeddings()
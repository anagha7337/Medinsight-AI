from langchain_community.document_loaders import PyPDFLoader, DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
import os

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

# Download embeddings
def download_hugging_face_embeddings():
    from huggingface_hub import InferenceClient

    class FixedHFEmbeddings:
        def __init__(self):
            self.client = InferenceClient(
                token=os.getenv("HUGGINGFACEHUB_API_TOKEN")
            )
            self.model = "sentence-transformers/all-MiniLM-L6-v2"

        def _get_vector(self, text):
            result = self.client.feature_extraction(text, model=self.model)
            if hasattr(result, 'tolist'):
                result = result.tolist()
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
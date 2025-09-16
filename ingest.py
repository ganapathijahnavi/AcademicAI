import os
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
# from langchain_community.embeddings import HuggingFaceEmbeddings   ❌ old
from langchain_huggingface import HuggingFaceEmbeddings              # ✅ new


# Load env
load_dotenv()

# Base pdf directory
base_dir = "pdfs"

docs = []
# Loop through all subject folders
for subject in os.listdir(base_dir):
    subject_path = os.path.join(base_dir, subject)
    if os.path.isdir(subject_path):  # only process folders
        for file in os.listdir(subject_path):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(subject_path, file)
                loader = PyPDFLoader(pdf_path)
                docs.extend(loader.load())

print(f"✅ Loaded {len(docs)} documents from {base_dir}")

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)

# Embeddings (free, local)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

# Store in Chroma
vectordb = Chroma.from_documents(chunks, embeddings, persist_directory="db")
vectordb.persist()

print("✅ Ingestion complete! All subject PDFs embedded and stored in db/")

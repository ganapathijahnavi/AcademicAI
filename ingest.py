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

<<<<<<< HEAD
 
all_chunks = []
all_metadatas = []
# Loop through all subject folders
for subject in os.listdir(base_dir):
    subject_path = os.path.join(base_dir, subject)
    if os.path.isdir(subject_path):
=======
docs = []
# Loop through all subject folders
for subject in os.listdir(base_dir):
    subject_path = os.path.join(base_dir, subject)
    if os.path.isdir(subject_path):  # only process folders
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
        for file in os.listdir(subject_path):
            if file.endswith(".pdf"):
                pdf_path = os.path.join(subject_path, file)
                loader = PyPDFLoader(pdf_path)
<<<<<<< HEAD
                docs = loader.load()
                # Add subject and filename as metadata
                for doc in docs:
                    doc.metadata["subject"] = subject
                    doc.metadata["source_file"] = file
                # Split into chunks
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=1000, chunk_overlap=200
                )
                chunks = text_splitter.split_documents(docs)
                for chunk in chunks:
                    all_chunks.append(chunk)
                    all_metadatas.append(chunk.metadata)

print(f"✅ Loaded and chunked {len(all_chunks)} chunks from {base_dir}")
=======
                docs.extend(loader.load())

print(f"✅ Loaded {len(docs)} documents from {base_dir}")

# Split into chunks
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
chunks = text_splitter.split_documents(docs)
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b

# Embeddings (free, local)
embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

<<<<<<< HEAD
# Store in Chroma with metadata
vectordb = Chroma.from_documents(all_chunks, embeddings, persist_directory="db")
vectordb.persist()

print("✅ Ingestion complete! All subject PDFs embedded and stored in db/ with metadata.")
=======
# Store in Chroma
vectordb = Chroma.from_documents(chunks, embeddings, persist_directory="chroma_db")

print("✅ Ingestion complete! All subject PDFs embedded and stored in chroma_db/ (auto-persisted)")
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b

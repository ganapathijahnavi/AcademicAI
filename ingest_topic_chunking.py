import os
import re
import fitz  # PyMuPDF
from dotenv import load_dotenv
from langchain_community.vectorstores import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Load env
load_dotenv()

# Base pdf directory
base_dir = "pdfs"

# Embedding model (recommended for technical/academic text)
embeddings = HuggingFaceEmbeddings(model_name="BAAI/bge-base-en-v1.5")

all_chunks = []

# Regex for heading detection (e.g., 3.1, 2.4.1, etc.)
HEADING_RE = re.compile(r"^(\d+(?:\.\d+)+)\s+(.+)")

for subject in os.listdir(base_dir):
    subject_upper = subject.upper()
    subject_path = os.path.join(base_dir, subject)
    if not os.path.isdir(subject_path):
        continue
    for file in os.listdir(subject_path):
        if not file.lower().endswith(".pdf"):
            continue
        pdf_path = os.path.join(subject_path, file)
        unit = os.path.splitext(file)[0].upper()  # e.g., UNIT-1
        doc = fitz.open(pdf_path)
        current_topic = None
        current_chunk = []
        current_metadata = None
        for page_num in range(len(doc)):
            page = doc[page_num]
            text = page.get_text("text")
            lines = text.splitlines()
            for line in lines:
                m = HEADING_RE.match(line.strip())
                if m:
                    # Save previous chunk
                    if current_chunk and current_metadata:
                        chunk_text = "\n".join(current_chunk).strip()
                        if chunk_text:
                            all_chunks.append({
                                "page_content": chunk_text,
                                "metadata": current_metadata.copy()
                            })
                    # Start new chunk
                    current_topic = m.group(2).strip()
                    current_metadata = {
                        "subject": subject_upper,
                        "unit": unit,
                        "topic": current_topic,
                        "page": page_num + 1,
                        "source": file
                    }
                    current_chunk = [line]
                else:
                    if current_chunk is not None:
                        current_chunk.append(line)
            # If no heading found on page, treat whole page as one chunk
            if not current_chunk:
                current_metadata = {
                    "subject": subject_upper,
                    "unit": unit,
                    "topic": f"Page {page_num+1}",
                    "page": page_num + 1,
                    "source": file
                }
                current_chunk = lines
        # Save last chunk
        if current_chunk and current_metadata:
            chunk_text = "\n".join(current_chunk).strip()
            if chunk_text:
                all_chunks.append({
                    "page_content": chunk_text,
                    "metadata": current_metadata.copy()
                })
        doc.close()

print(f"✅ Loaded and chunked {len(all_chunks)} topic-based chunks from {base_dir}")

# Convert to LangChain Document objects
from langchain_core.documents import Document
lc_chunks = [Document(page_content=chunk["page_content"], metadata=chunk["metadata"]) for chunk in all_chunks]

# Store in Chroma with metadata
vectordb = Chroma.from_documents(lc_chunks, embeddings, persist_directory="db", collection_name="engineering_notes")
vectordb.persist()

print("✅ Ingestion complete! All subject PDFs embedded and stored in db/ with topic-based metadata.")

# app.py
import os
import re
import logging
from typing import Any
from threading import Lock

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# -------------- logging --------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------- FastAPI setup --------------
app = FastAPI(title="Subject QA Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, set a specific origin
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------- Check OPENAI_API_KEY --------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("Please set the OPENAI_API_KEY environment variable.")

try:
    OPENAI_API_KEY.encode("ascii")
except UnicodeEncodeError:
    raise ValueError(
        "OPENAI_API_KEY contains non-ASCII characters. Copy it exactly as given by OpenAI."
    )

# -------------- Lazy initialization globals --------------
qa = None
_init_lock = Lock()

# make a cache dir for huggingface / sentence-transformers
HF_CACHE_DIR = os.environ.get("HF_CACHE_DIR", "./hf_cache")
os.makedirs(HF_CACHE_DIR, exist_ok=True)


def get_qa():
    """
    Initialize embeddings/vectorstore/LLM/QA only once, safely (thread-locked).
    """
    global qa
    if qa is not None:
        return qa

    with _init_lock:
        if qa is not None:
            return qa

        # ensure huggingface/transformers cache env vars point to a real folder
        os.environ.setdefault("TRANSFORMERS_CACHE", HF_CACHE_DIR)
        os.environ.setdefault("HF_HOME", HF_CACHE_DIR)
        os.environ.setdefault("SENTENCE_TRANSFORMERS_HOME", HF_CACHE_DIR)

        # --- Automatic ingestion if chroma_db/ is missing or empty ---
        chroma_dir = "./chroma_db"
        needs_ingest = not os.path.exists(chroma_dir) or not os.listdir(chroma_dir)
        if needs_ingest:
            logger.info("chroma_db/ missing or empty. Running automatic ingestion...")
            try:
                from langchain_community.document_loaders import PyPDFLoader
                from langchain.text_splitter import RecursiveCharacterTextSplitter
                from langchain_huggingface import HuggingFaceEmbeddings
                from langchain_chroma import Chroma
                # Ingest all PDFs from ./pdfs
                base_dir = "pdfs"
                docs = []
                for subject in os.listdir(base_dir):
                    subject_path = os.path.join(base_dir, subject)
                    if os.path.isdir(subject_path):
                        for file in os.listdir(subject_path):
                            if file.endswith(".pdf"):
                                pdf_path = os.path.join(subject_path, file)
                                loader = PyPDFLoader(pdf_path)
                                docs.extend(loader.load())
                logger.info(f"Loaded {len(docs)} documents from {base_dir}")
                text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
                chunks = text_splitter.split_documents(docs)
                embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
                Chroma.from_documents(chunks, embeddings, persist_directory=chroma_dir)
                logger.info("Ingestion complete! PDFs embedded and stored in chroma_db/ (auto-persisted)")
            except Exception as e:
                logger.exception("Automatic ingestion failed. QA chain will not be available.")
                raise

        logger.info("Initializing embeddings, Chroma, LLM, and QA chain...")
        try:
            from langchain_huggingface import HuggingFaceEmbeddings
            from langchain_chroma import Chroma
            from langchain_openai import ChatOpenAI
            from langchain.chains import RetrievalQA
        except Exception:
            logger.exception("Failed to import LangChain provider libraries.")
            raise

        try:
            try:
                embedding_function = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2",
                    model_kwargs={"device": "cpu", "cache_folder": HF_CACHE_DIR},
                )
            except TypeError:
                embedding_function = HuggingFaceEmbeddings(
                    model_name="sentence-transformers/all-MiniLM-L6-v2"
                )

            vectordb = Chroma(
                collection_name="my_collection",
                embedding_function=embedding_function,
                persist_directory=chroma_dir,
            )

            llm = ChatOpenAI(
                model_name="gpt-4o-mini",
                temperature=0,
                openai_api_key=OPENAI_API_KEY,
            )

            qa_instance = RetrievalQA.from_chain_type(
                llm=llm,
                retriever=vectordb.as_retriever(),
                chain_type="stuff",
            )

            qa = qa_instance
            logger.info("QA chain initialized successfully.")
            return qa

        except Exception:
            logger.exception("Failed during QA chain initialization.")
            qa = None
            raise


# -------------- Request model --------------
class Query(BaseModel):
    question: str


# -------------- Helpers --------------
def coerce_result_to_text(res: Any) -> str:
    if res is None:
        return ""
    if isinstance(res, str):
        return res
    if isinstance(res, dict):
        for key in ("answer", "result", "output_text", "text"):
            v = res.get(key)
            if isinstance(v, str):
                return v
        try:
            return " ".join(str(v) for v in res.values())
        except Exception:
            return str(res)
    if isinstance(res, (list, tuple)):
        return "\n\n".join(coerce_result_to_text(x) for x in res)
    return str(res)


def collapse_blank_lines(s: str) -> str:
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    return s.strip()


# -------------- Endpoints --------------
@app.get("/")
def root():
    return {"message": "FastAPI backend running. Use POST /ask to query."}


@app.options("/ask")
def ask_options():
    # allow preflight to succeed quickly
    return JSONResponse(content={"ok": True})


@app.post("/ask")
def ask_endpoint(query: Query):
    try:
        qa_instance = get_qa()
        # Try common invocation patterns
        try:
            result = qa_instance.invoke({"query": query.question})
        except TypeError:
            try:
                result = qa_instance.invoke(query.question)
            except Exception:
                result = qa_instance.run(query.question)
        except Exception:
            result = qa_instance.run(query.question)

        result_text = coerce_result_to_text(result)
        result_text = collapse_blank_lines(result_text)
        result_text = result_text.encode("utf-8", errors="replace").decode("utf-8")

        return JSONResponse(content={"answer": result_text})
    except Exception as e:
        # log full traceback server-side
        logger.exception("Error in /ask endpoint")
        # return a friendly error message (keeps axios from throwing)
        return JSONResponse(content={"answer": f"Error: {str(e)}"})


# -------------- Start uvicorn when running directly --------------
if __name__ == "__main__":
    import uvicorn

    port = int(os.environ.get("PORT", 7860))
    uvicorn.run("app:app", host="0.0.0.0", port=port)

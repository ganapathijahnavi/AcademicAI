# app.py
import os
import re
import logging
from typing import Any
<<<<<<< HEAD
=======
from threading import Lock
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

<<<<<<< HEAD
# langchain provider-specific packages (use the versions you installed)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import openai

=======
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
# -------------- logging --------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------- FastAPI setup --------------
app = FastAPI(title="Subject QA Bot API")

app.add_middleware(
    CORSMiddleware,
<<<<<<< HEAD
    allow_origins=["*"],  # in production, set your frontend URL instead of "*"
=======
    allow_origins=["*"],  # in production, set a specific origin
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
    allow_methods=["*"],
    allow_headers=["*"],
)

<<<<<<< HEAD


# -------------- Embeddings, Vector DB, LLM (Transformers) --------------
try:

    embedding_function = HuggingFaceEmbeddings(
        model_name="BAAI/bge-base-en-v1.5"
    )

    vectordb = Chroma(
        collection_name="engineering_notes",
        embedding_function=embedding_function,
        persist_directory="db",
    )

    # Configure OpenRouter (OpenAI-compatible)
    OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
    if not OPENROUTER_API_KEY:
        raise ValueError("Please set the OPENROUTER_API_KEY environment variable before starting the server.")
    OPENROUTER_MODEL = os.environ.get("OPENROUTER_MODEL", "openai/gpt-3.5-turbo")
    client = openai.OpenAI(
        api_key=OPENROUTER_API_KEY,
        base_url="https://openrouter.ai/api/v1"
    )
except Exception as e:
    logger.exception("Error initializing embeddings/vectorstore/LLM/QA chain")
    raise
=======
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

>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b

# -------------- Request model --------------
class Query(BaseModel):
    question: str

<<<<<<< HEAD
# -------------- Helpers --------------
def coerce_result_to_text(res: Any) -> str:
    """
    Turn various langchain result shapes into a usable string.
    """
=======

# -------------- Helpers --------------
def coerce_result_to_text(res: Any) -> str:
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
    if res is None:
        return ""
    if isinstance(res, str):
        return res
    if isinstance(res, dict):
<<<<<<< HEAD
        # common keys used by chains
=======
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
        for key in ("answer", "result", "output_text", "text"):
            v = res.get(key)
            if isinstance(v, str):
                return v
<<<<<<< HEAD
        # fallback: join stringified values
=======
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
        try:
            return " ".join(str(v) for v in res.values())
        except Exception:
            return str(res)
    if isinstance(res, (list, tuple)):
        return "\n\n".join(coerce_result_to_text(x) for x in res)
    return str(res)

<<<<<<< HEAD
def collapse_blank_lines(s: str) -> str:
    # replace runs of 3+ blank lines with exactly 2 newlines, and trim edges
    s = re.sub(r'\n\s*\n\s*\n+', '\n\n', s)
    return s.strip()

=======

def collapse_blank_lines(s: str) -> str:
    s = re.sub(r"\n\s*\n\s*\n+", "\n\n", s)
    return s.strip()


>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b
# -------------- Endpoints --------------
@app.get("/")
def root():
    return {"message": "FastAPI backend running. Use POST /ask to query."}


<<<<<<< HEAD
@app.post("/ask")
def ask_endpoint(query: Query):
    """
    Accepts JSON: { "question": "..." }
    Returns JSON: { "answer": "..." }  (always a string)
    """
    try:

        # Retrieve context from ChromaDB


        # --- Metadata filtering: try to detect subject/unit/topic from question (simple heuristic) ---
        filters = {}
        q_lower = query.question.lower()
        # Example: if user asks about dbms or os, filter subject
        for subj in ["dbms", "os", "bda", "ml", "python", "java", "cn", "dsa", "dl", "se", "fsad", "flat", "ethical", "ip", "dwdm", "cd", "cns", "ds", "cc"]:
            if subj in q_lower:
                filters["subject"] = subj.upper()
        # Example: if user mentions unit-1, unit 2, etc.
        import re
        unit_match = re.search(r"unit[- ]?(\d+)", q_lower)
        if unit_match:
            filters["unit"] = f"UNIT-{unit_match.group(1)}"
        # Example: if user mentions a topic (very basic, can be improved)
        # (You can add more advanced NLP here)

        retriever = vectordb.as_retriever()
        # If filters found, use flat dict of field: {"$eq": value} for ChromaDB compatibility
        if filters:
            where = {k: {"$eq": v} for k, v in filters.items()}
            logger.info(f"Using filters: {where}")
            docs = retriever.invoke(query.question, filter=where)
        else:
            logger.info("No filters used.")
            docs = retriever.invoke(query.question)

        # Log number of docs retrieved
        if isinstance(docs, list):
            logger.info(f"Retrieved {len(docs)} docs.")
        else:
            logger.info(f"Retrieved 1 doc.")

        if isinstance(docs, list):
            context = "\n".join([doc.page_content for doc in docs])
        else:
            context = docs.page_content if hasattr(docs, "page_content") else str(docs)

        # Log the context and metadata for debugging RAG
        logger.info("RAG Context:\n%s", context)
        if isinstance(docs, list):
            for i, doc in enumerate(docs):
                logger.info(f"Doc {i} metadata: {getattr(doc, 'metadata', {})}")
        else:
            logger.info(f"Doc metadata: {getattr(docs, 'metadata', {})}")


        # Compose prompt and handle fallback if context is empty
        if context.strip():
            prompt = (
                "You are an academic assistant. Use the context below to answer the question. "
                "If the context is helpful, use it. If not, answer as best as you can using your own knowledge. "
                "If the answer contains code, always format it as a markdown code block with the correct language.\n"
                f"Context:\n{context}\n\nQuestion: {query.question}\nAnswer:"
            )
            logger.info("RAG Prompt:\n%s", prompt)
            system_message = "You are an academic assistant. Use the provided context if it is helpful, otherwise answer using your own knowledge. If the answer contains code, always format it as a markdown code block with the correct language."
            temperature = 0.2
        else:
            prompt = (
                f"{query.question}\n"
                "If the answer contains code, always format it as a markdown code block with the correct language."
            )
            logger.info("No RAG context, falling back to LLM only. Prompt:\n%s", prompt)
            system_message = (
                "You are an expert academic assistant. Always answer the question as best as you can, "
                "even if you have to use your own knowledge. Never say 'I don't know.' "
                "If the answer contains code, always format it as a markdown code block with the correct language."
            )
            temperature = 0.7

        response = client.chat.completions.create(
            model=OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": prompt},
            ],
            temperature=temperature,
        )
        answer = response.choices[0].message.content
        logger.info("Raw LLM answer before formatting:\n%s", answer)

        answer = collapse_blank_lines(answer)
        answer = answer.encode("utf-8", errors="replace").decode("utf-8")
        return JSONResponse(content={"answer": answer})

    except Exception as e:
        logger.exception("Error in /ask endpoint")
        return JSONResponse(content={"answer": f"Error: {str(e)}"})
=======
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
>>>>>>> 0e5c0db416bfc4f7a9669cbb80e230707f4fa23b

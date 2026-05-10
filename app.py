# app.py
import os
import re
import logging
from typing import Any

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# langchain provider-specific packages (use the versions you installed)
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
import openai

# -------------- logging --------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -------------- FastAPI setup --------------
app = FastAPI(title="Subject QA Bot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, set your frontend URL instead of "*"
    allow_methods=["*"],
    allow_headers=["*"],
)



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

# -------------- Request model --------------
class Query(BaseModel):
    question: str

# -------------- Helpers --------------
def coerce_result_to_text(res: Any) -> str:
    """
    Turn various langchain result shapes into a usable string.
    """
    if res is None:
        return ""
    if isinstance(res, str):
        return res
    if isinstance(res, dict):
        # common keys used by chains
        for key in ("answer", "result", "output_text", "text"):
            v = res.get(key)
            if isinstance(v, str):
                return v
        # fallback: join stringified values
        try:
            return " ".join(str(v) for v in res.values())
        except Exception:
            return str(res)
    if isinstance(res, (list, tuple)):
        return "\n\n".join(coerce_result_to_text(x) for x in res)
    return str(res)

def collapse_blank_lines(s: str) -> str:
    # replace runs of 3+ blank lines with exactly 2 newlines, and trim edges
    s = re.sub(r'\n\s*\n\s*\n+', '\n\n', s)
    return s.strip()

# -------------- Endpoints --------------
@app.get("/")
def root():
    return {"message": "FastAPI backend running. Use POST /ask to query."}


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

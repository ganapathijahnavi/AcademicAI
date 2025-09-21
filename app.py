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
from langchain_openai import ChatOpenAI
from langchain.chains import RetrievalQA

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

# -------------- Check OPENAI_API_KEY --------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError(
        "Please set the OPENAI_API_KEY environment variable before starting the server."
        " Example (PowerShell): $env:OPENAI_API_KEY='sk-...'\n"
        "On Windows (CMD): setx OPENAI_API_KEY \"sk-...\"  (then restart your terminal)\n"
        "On macOS/Linux: export OPENAI_API_KEY='sk-...'\n"
    )

# If a user accidentally copied smart/curly quotes or other non-ascii chars, fail early with a clear message:
try:
    OPENAI_API_KEY.encode("ascii")
except UnicodeEncodeError:
    raise ValueError(
        "OPENAI_API_KEY contains non-ASCII characters (curly quotes or stray characters). "
        "Make sure you set the key exactly as provided by OpenAI with plain ASCII characters."
    )

# -------------- Embeddings, Vector DB, LLM, QA chain --------------
try:
    embedding_function = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

    vectordb = Chroma(
        collection_name="my_collection",
        embedding_function=embedding_function,
        persist_directory="./chroma_db",
    )

    llm = ChatOpenAI(
        model_name="gpt-4o-mini",
        temperature=0,
        openai_api_key=OPENAI_API_KEY,
    )

    qa = RetrievalQA.from_chain_type(
        llm=llm,
        retriever=vectordb.as_retriever(),
        chain_type="stuff",
    )
except Exception as e:
    logger.exception("Error initializing embeddings/vectorstore/LLM/QA chain")
    # re-raise so the user sees startup error
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
        # Try common invocation patterns: prefer dict-style invoke, fallback to string invoke, then .run()
        try:
            result = qa.invoke({"query": query.question})
        except TypeError:
            try:
                result = qa.invoke(query.question)
            except Exception:
                # final fallback
                result = qa.run(query.question)
        except Exception:
            # some other invoke error — try run
            result = qa.run(query.question)

        # coerce to text (so frontend won't receive an object)
        result_text = coerce_result_to_text(result)

        # collapse noisy blank lines and make sure we have UTF-8-safe string
        result_text = collapse_blank_lines(result_text)
        result_text = result_text.encode("utf-8", errors="replace").decode("utf-8")

        return JSONResponse(content={"answer": result_text})

    except Exception as e:
        # Log full traceback server-side
        logger.exception("Error in /ask endpoint")
        # Return textual error string so the frontend can show it (keeps axios from throwing)
        return JSONResponse(content={"answer": f"Error: {str(e)}"})

# -------------- Start uvicorn when running directly --------------
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))  # Render sets $PORT
    uvicorn.run("app:app", host="0.0.0.0", port=port)

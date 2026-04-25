# # # app.py
# # import os
# # import re
# # import logging
# # from typing import Any

# # from fastapi import FastAPI
# # from fastapi.middleware.cors import CORSMiddleware
# # from fastapi.responses import JSONResponse
# # from pydantic import BaseModel

# # # langchain provider-specific packages (use the versions you installed)
# # from langchain_huggingface import HuggingFaceEmbeddings
# # from langchain_chroma import Chroma
# # from langchain_openai import ChatOpenAI
# # from langchain.chains import RetrievalQA

# # # -------------- logging --------------
# # logging.basicConfig(level=logging.INFO)
# # logger = logging.getLogger(__name__)

# # # -------------- FastAPI setup --------------
# # app = FastAPI(title="Subject QA Bot API")

# # app.add_middleware(
# #     CORSMiddleware,
# #     allow_origins=["*"],  # in production, set your frontend URL instead of "*"
# #     allow_methods=["*"],
# #     allow_headers=["*"],
# # )

# # # -------------- Check OPENAI_API_KEY --------------
# # OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# # if not OPENAI_API_KEY:
# #     raise ValueError(
# #         "Please set the OPENAI_API_KEY environment variable before starting the server."
# #         " Example (PowerShell): $env:OPENAI_API_KEY='sk-...'\n"
# #         "On Windows (CMD): setx OPENAI_API_KEY \"sk-...\"  (then restart your terminal)\n"
# #         "On macOS/Linux: export OPENAI_API_KEY='sk-...'\n"
# #     )

# # # If a user accidentally copied smart/curly quotes or other non-ascii chars, fail early with a clear message:
# # try:
# #     OPENAI_API_KEY.encode("ascii")
# # except UnicodeEncodeError:
# #     raise ValueError(
# #         "OPENAI_API_KEY contains non-ASCII characters (curly quotes or stray characters). "
# #         "Make sure you set the key exactly as provided by OpenAI with plain ASCII characters."
# #     )

# # # -------------- Embeddings, Vector DB, LLM, QA chain --------------
# # try:
# #     embedding_function = HuggingFaceEmbeddings(
# #         model_name="sentence-transformers/all-MiniLM-L6-v2"
# #     )

# #     vectordb = Chroma(
# #         collection_name="my_collection",
# #         embedding_function=embedding_function,
# #         persist_directory="./chroma_db",
# #     )

# #     llm = ChatOpenAI(
# #         model_name="gpt-4o-mini",
# #         temperature=0,
# #         openai_api_key=OPENAI_API_KEY,
# #     )

# #     qa = RetrievalQA.from_chain_type(
# #         llm=llm,
# #         retriever=vectordb.as_retriever(),
# #         chain_type="stuff",
# #     )
# # except Exception as e:
# #     logger.exception("Error initializing embeddings/vectorstore/LLM/QA chain")
# #     # re-raise so the user sees startup error
# #     raise

# # # -------------- Request model --------------
# # class Query(BaseModel):
# #     question: str

# # # -------------- Helpers --------------
# # def coerce_result_to_text(res: Any) -> str:
# #     """
# #     Turn various langchain result shapes into a usable string.
# #     """
# #     if res is None:
# #         return ""
# #     if isinstance(res, str):
# #         return res
# #     if isinstance(res, dict):
# #         # common keys used by chains
# #         for key in ("answer", "result", "output_text", "text"):
# #             v = res.get(key)
# #             if isinstance(v, str):
# #                 return v
# #         # fallback: join stringified values
# #         try:
# #             return " ".join(str(v) for v in res.values())
# #         except Exception:
# #             return str(res)
# #     if isinstance(res, (list, tuple)):
# #         return "\n\n".join(coerce_result_to_text(x) for x in res)
# #     return str(res)

# # def collapse_blank_lines(s: str) -> str:
# #     # replace runs of 3+ blank lines with exactly 2 newlines, and trim edges
# #     s = re.sub(r'\n\s*\n\s*\n+', '\n\n', s)
# #     return s.strip()

# # # -------------- Endpoints --------------
# # @app.get("/")
# # def root():
# #     return {"message": "FastAPI backend running. Use POST /ask to query."}


# # @app.post("/ask")
# # def ask_endpoint(query: Query):
# #     """
# #     Accepts JSON: { "question": "..." }
# #     Returns JSON: { "answer": "..." }  (always a string)
# #     """
# #     try:
# #         # Try common invocation patterns: prefer dict-style invoke, fallback to string invoke, then .run()
# #         try:
# #             result = qa.invoke({"query": query.question})
# #         except TypeError:
# #             try:
# #                 result = qa.invoke(query.question)
# #             except Exception:
# #                 # final fallback
# #                 result = qa.run(query.question)
# #         except Exception:
# #             # some other invoke error — try run
# #             result = qa.run(query.question)

# #         # coerce to text (so frontend won't receive an object)
# #         result_text = coerce_result_to_text(result)

# #         # collapse noisy blank lines and make sure we have UTF-8-safe string
# #         result_text = collapse_blank_lines(result_text)
# #         result_text = result_text.encode("utf-8", errors="replace").decode("utf-8")

# #         return JSONResponse(content={"answer": result_text})

# #     except Exception as e:
# #         # Log full traceback server-side
# #         logger.exception("Error in /ask endpoint")
# #         # Return textual error string so the frontend can show it (keeps axios from throwing)
# #         return JSONResponse(content={"answer": f"Error: {str(e)}"})

# # # -------------- Start uvicorn when running directly --------------
# # if __name__ == "__main__":
# #     import uvicorn
# #     port = int(os.environ.get("PORT", 8000))  # Render sets $PORT
# #     uvicorn.run("app:app", host="0.0.0.0", port=port)

# # app.py
# import os
# import re
# import logging
# from typing import Any

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from fastapi.responses import JSONResponse
# from pydantic import BaseModel

# # langchain provider-specific packages
# from langchain_huggingface import HuggingFaceEmbeddings
# from langchain_chroma import Chroma
# from langchain_openai import ChatOpenAI
# from langchain.chains import RetrievalQA

# # -------------- logging --------------
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)

# # -------------- FastAPI setup --------------
# app = FastAPI(title="Subject QA Bot API")

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # in production, replace "*" with your frontend domain
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # -------------- Check OPENAI_API_KEY --------------
# OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
# if not OPENAI_API_KEY:
#     raise ValueError("Please set the OPENAI_API_KEY environment variable.")

# try:
#     OPENAI_API_KEY.encode("ascii")
# except UnicodeEncodeError:
#     raise ValueError(
#         "OPENAI_API_KEY contains non-ASCII characters. "
#         "Copy it exactly as given by OpenAI."
#     )

# # -------------- Lazy initialization globals --------------
# qa = None  # cache for QA chain

# def get_qa():
#     """Initialize embeddings/vector DB/LLM only once, on first request."""
#     global qa
#     if qa is None:
#         logger.info("Initializing embeddings, Chroma, LLM, and QA chain...")

#         embedding_function = HuggingFaceEmbeddings(
#             model_name="sentence-transformers/all-MiniLM-L6-v2"
#         )

#         vectordb = Chroma(
#             collection_name="my_collection",
#             embedding_function=embedding_function,
#             persist_directory="./chroma_db",
#         )

#         llm = ChatOpenAI(
#             model_name="gpt-4o-mini",
#             temperature=0,
#             openai_api_key=OPENAI_API_KEY,
#         )

#         qa = RetrievalQA.from_chain_type(
#             llm=llm,
#             retriever=vectordb.as_retriever(),
#             chain_type="stuff",
#         )
#         logger.info("QA chain initialized successfully.")
#     return qa

# # -------------- Request model --------------
# class Query(BaseModel):
#     question: str

# # -------------- Helpers --------------
# def coerce_result_to_text(res: Any) -> str:
#     """Convert various langchain result shapes into plain string."""
#     if res is None:
#         return ""
#     if isinstance(res, str):
#         return res
#     if isinstance(res, dict):
#         for key in ("answer", "result", "output_text", "text"):
#             v = res.get(key)
#             if isinstance(v, str):
#                 return v
#         try:
#             return " ".join(str(v) for v in res.values())
#         except Exception:
#             return str(res)
#     if isinstance(res, (list, tuple)):
#         return "\n\n".join(coerce_result_to_text(x) for x in res)
#     return str(res)

# def collapse_blank_lines(s: str) -> str:
#     s = re.sub(r'\n\s*\n\s*\n+', '\n\n', s)
#     return s.strip()

# # -------------- Endpoints --------------
# @app.get("/")
# def root():
#     return {"message": "FastAPI backend running. Use POST /ask to query."}

# @app.post("/ask")
# def ask_endpoint(query: Query):
#     try:
#         qa_instance = get_qa()
#         try:
#             result = qa_instance.invoke({"query": query.question})
#         except TypeError:
#             try:
#                 result = qa_instance.invoke(query.question)
#             except Exception:
#                 result = qa_instance.run(query.question)
#         except Exception:
#             result = qa_instance.run(query.question)

#         result_text = coerce_result_to_text(result)
#         result_text = collapse_blank_lines(result_text)
#         result_text = result_text.encode("utf-8", errors="replace").decode("utf-8")

#         return JSONResponse(content={"answer": result_text})
#     except Exception as e:
#         logger.exception("Error in /ask endpoint")
#         return JSONResponse(content={"answer": f"Error: {str(e)}"})

# # -------------- Start uvicorn when running directly --------------
# if __name__ == "__main__":
#     import uvicorn
#     port = int(os.environ.get("PORT", 8000))  # Render sets $PORT
#     uvicorn.run("app:app", host="0.0.0.0", port=port)



import React, { useState, useEffect, useRef } from "react";
import axios from "axios";
import ReactMarkdown from "react-markdown";
import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";
import { v4 as uuidv4 } from "uuid";
import "./App.css";

function App() {
  const [sessions, setSessions] = useState([]);
  const [activeSessionId, setActiveSessionId] = useState(null);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");
  const [replyTo, setReplyTo] = useState(null); // ✅ reply preview state
  const chatEndRef = useRef(null);

  const themeStyles = {
    background: darkMode ? "#1e1e1e" : "#fff",
    color: darkMode ? "#f5f5f5" : "#000",
  };

  const chatBubbleStyle = {
    background: darkMode ? "#25D366" : "#4CAF50",
    color: "#fff",
    padding: "0.75rem 1rem",
    borderRadius: "18px",
    position: "relative",
    alignSelf: "flex-end",
    maxWidth: "70%",
    marginBottom: "0.5rem",
    wordBreak: "break-word",
  };

  const activeSession = sessions.find((s) => s.id === activeSessionId);

  const handleAsk = async () => {
    if (!question) return;

    let sessionId = activeSessionId;
    if (!sessionId) {
      const newSessionId = uuidv4();
      const newSession = {
        id: newSessionId,
        title:
          question.length > 30 ? question.slice(0, 30) + "..." : question,
        messages: [],
      };
      setSessions((prev) => [newSession, ...prev]);
      setActiveSessionId(newSessionId);
      sessionId = newSessionId;
    }

    setLoading(true);
    try {
      const response = await axios.post(
        "https://ganapati-jahnavi-academicai-backend.hf.space/ask",
        { question }
      );
      const answer = response.data.answer;

      setSessions((prev) =>
        prev.map((session) =>
          session.id === sessionId
            ? {
                ...session,
                messages: [
                  ...session.messages,
                  { question, answer, replyTo }, // ✅ store reply link
                ],
              }
            : session
        )
      );
    } catch (err) {
      console.error(err);
      setSessions((prev) =>
        prev.map((session) =>
          session.id === sessionId
            ? {
                ...session,
                messages: [
                  ...session.messages,
                  {
                    question,
                    answer: "Error fetching answer from backend.",
                    replyTo,
                  },
                ],
              }
            : session
        )
      );
    }
    setQuestion("");
    setReplyTo(null); // clear reply after asking
    setLoading(false);
  };

  const CopyButton = ({ text }) => {
    const [copied, setCopied] = useState(false);
    const handleCopy = () => {
      navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };
    return (
      <button className="copy-btn" onClick={handleCopy}>
        {copied ? "Copied!" : "Copy"}
      </button>
    );
  };

  const ActionButtons = ({ answer, question }) => {
    const [copied, setCopied] = useState(false);

    const handleCopyAll = () => {
      navigator.clipboard.writeText(answer);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    };

    return (
      <div className="bot-actions">
        <button onClick={handleCopyAll}>{copied ? "Copied!" : "Copy"}</button>
        <button onClick={() => setReplyTo({ question, answer })}>Reply</button>
      </div>
    );
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [activeSession?.messages, loading]);

  const createNewSession = () => {
    const newSessionId = uuidv4();
    const newSession = { id: newSessionId, title: "New Chat", messages: [] };
    setSessions((prev) => [newSession, ...prev]);
    setActiveSessionId(newSessionId);
  };

  useEffect(() => {
    if (!activeSession || activeSession.messages.length === 0) return;
    const firstMessage = activeSession.messages[0].question;
    const newTitle =
      firstMessage.length > 30
        ? firstMessage.slice(0, 30) + "..."
        : firstMessage;
    setSessions((prev) =>
      prev.map((s) =>
        s.id === activeSession.id && s.title === "New Chat"
          ? { ...s, title: newTitle }
          : s
      )
    );
  }, [activeSession, activeSession?.messages]);

  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        fontFamily: "Arial, sans-serif",
        ...themeStyles,
      }}
    >
      {/* Sidebar */}
      <div className="sidebar">
        <img
          src="/ACADEMIC.png"
          alt="GPT Logo"
          style={{ width: "120px", marginBottom: "1rem" }}
        />
        <div className="description">
          <p
            style={{
              fontSize: "0.9rem",
              color: darkMode ? "#f5f5f5" : "#333",
              lineHeight: "1.4rem",
            }}
          >
            Your AI Study Buddy — Get summaries, simple explanations, and
            topic-focused answers. Learn smarter, faster, and easier with our
            education-powered "AcademicAI".
          </p>
        </div>
        <button className="new-chat-btn" onClick={createNewSession}>
          + New Chat
        </button>
        <input
          type="text"
          placeholder="Search chats..."
          onChange={(e) => setSearchTerm(e.target.value)}
          className="search-bar"
        />
        <div className="history-header">
          <h3>History</h3>
          <button
            className="mode-toggle"
            onClick={() => setDarkMode(!darkMode)}
          >
            {darkMode ? "☀️" : "🌙"}
          </button>
        </div>
        <div className="history-list">
          {sessions
            .filter((session) =>
              session.title.toLowerCase().includes(searchTerm.toLowerCase())
            )
            .map((session) => (
              <div
                key={session.id}
                className={`session-item ${
                  session.id === activeSessionId ? "active" : ""
                }`}
                onClick={() => setActiveSessionId(session.id)}
              >
                {session.title} ({session.messages.length} messages)
              </div>
            ))}
        </div>
      </div>

      {/* Chat Window */}
      <div className="chat-window">
        <div className="chat-messages">
          {activeSession?.messages.map((chat, idx) => (
            <div key={idx} className="chat-block">
              {/* User Message */}
              <div style={chatBubbleStyle}>
                <strong>You:</strong> {chat.question}
              </div>

              {/* Bot Message */}
              <div className="bot-message">
                <img src="/agent.png" alt="GPT" className="bot-avatar" />
                <div className="bot-content">
                  <ReactMarkdown
                    components={{
                      p({ children }) {
                        return (
                          <p style={{ margin: "0.5rem 0", lineHeight: "1.5" }}>
                            {children}
                          </p>
                        );
                      },
                      code({ inline, className, children, ...props }) {
                        const match = /language-(\w+)/.exec(className || "");
                        const codeText = String(children).replace(/\n$/, "");
                        return !inline ? (
                          <div className="code-block">
                            <CopyButton text={codeText} />
                            <SyntaxHighlighter
                              style={oneDark}
                              language={match ? match[1] : "text"}
                              PreTag="div"
                              {...props}
                            >
                              {codeText}
                            </SyntaxHighlighter>
                          </div>
                        ) : (
                          <code className="inline-code" {...props}>
                            {children}
                          </code>
                        );
                      },
                    }}
                  >
                    {chat.answer}
                  </ReactMarkdown>

                  {/* Action buttons for bot message */}
                  <ActionButtons answer={chat.answer} question={chat.question} />
                </div>
              </div>
            </div>
          ))}
          {loading && <p>Loading...</p>}
          <div ref={chatEndRef} />
        </div>

        {/* Reply Preview above Input */}
        {replyTo && (
          <div className="reply-preview">
            <strong>Replying to:</strong>{" "}
            {replyTo.answer.length > 80
              ? replyTo.answer.slice(0, 80) + "..."
              : replyTo.answer}
            <button className="close-reply" onClick={() => setReplyTo(null)}>
              ✖
            </button>
          </div>
        )}

        {/* Input Bar */}
        <div
          style={{
            display: "flex",
            justifyContent: "center",
            padding: "1rem",
            borderTop: darkMode ? "1px solid #333" : "1px solid #ddd",
            background: darkMode ? "#1b1b1b" : "#f9f9f9",
          }}
        >
          <div className="input-bar">
            <input
              type="text"
              value={question}
              onChange={(e) => setQuestion(e.target.value)}
              placeholder="Type your question..."
              onKeyDown={(e) => e.key === "Enter" && handleAsk()}
            />
            <button onClick={handleAsk}>➜</button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;


// // import React, { useState } from "react";
// // import axios from "axios";

// // function App() {
// //   const [question, setQuestion] = useState("");
// //   const [answer, setAnswer] = useState("");
// //   const [loading, setLoading] = useState(false);

// //   const handleAsk = async () => {
// //     if (!question.trim()) return;
// //     setLoading(true);
// //     setAnswer("");

// //     try {
// //       const response = await axios.post("http://127.0.0.1:8000/ask", { question });
// //       setAnswer(response.data.answer || "No answer returned.");
// //     } catch (err) {
// //       console.error(err);
// //       setAnswer("❌ Error fetching answer from backend.");
// //     }

// //     setLoading(false);
// //   };

// //   return (
// //     <div
// //       style={{
// //         padding: "2rem",
// //         fontFamily: "Arial",
// //         maxWidth: "700px",
// //         margin: "0 auto",
// //       }}
// //     >
// //       <h1 style={{ textAlign: "center" }}>📘 Subject QA Bot</h1>

// //       <div style={{ display: "flex", marginTop: "1rem" }}>
// //         <input
// //           type="text"
// //           value={question}
// //           onChange={(e) => setQuestion(e.target.value)}
// //           placeholder="Ask me anything..."
// //           style={{
// //             flex: 1,
// //             padding: "0.7rem",
// //             border: "1px solid #ccc",
// //             borderRadius: "8px",
// //           }}
// //         />
// //         <button
// //           onClick={handleAsk}
// //           style={{
// //             padding: "0.7rem 1.5rem",
// //             marginLeft: "1rem",
// //             backgroundColor: "#007bff",
// //             color: "white",
// //             border: "none",
// //             borderRadius: "8px",
// //             cursor: "pointer",
// //           }}
// //         >
// //           Ask
// //         </button>
// //       </div>

// //       <div
// //         style={{
// //           marginTop: "2rem",
// //           backgroundColor: "#f9f9f9",
// //           padding: "1rem",
// //           borderRadius: "8px",
// //           minHeight: "80px",
// //         }}
// //       >
// //         <h3>Answer:</h3>
// //         {loading ? <p>⏳ Thinking...</p> : <p>{answer}</p>}
// //       </div>
// //     </div>
// //   );
// // }

// // export default App;



// import React, { useState } from "react";
// import axios from "axios";

// function App() {
//   const [question, setQuestion] = useState("");
//   const [messages, setMessages] = useState([]); // chat history
//   const [loading, setLoading] = useState(false);

//   const handleAsk = async () => {
//     if (!question) return;
//     const newMessage = { sender: "user", text: question };
//     setMessages([...messages, newMessage]);
//     setQuestion("");
//     setLoading(true);

//     try {
//       const response = await axios.post("http://127.0.0.1:8000/ask", { question });
//       const botMessage = { sender: "bot", text: response.data.answer };
//       setMessages((prev) => [...prev, botMessage]);
//     } catch (err) {
//       console.error(err);
//       setMessages((prev) => [...prev, { sender: "bot", text: "Error fetching answer." }]);
//     }

//     setLoading(false);
//   };

//   return (
//     <div style={{ display: "flex", height: "100vh", fontFamily: "Arial" }}>
//       {/* Sidebar */}
//       <div
//         style={{
//           width: "250px",
//           backgroundColor: "#f4f4f4",
//           padding: "1rem",
//           borderRight: "1px solid #ccc",
//           overflowY: "auto",
//         }}
//       >
//         <h3>📜 History</h3>
//         <ul style={{ listStyle: "none", padding: 0 }}>
//           {messages
//             .filter((m) => m.sender === "user")
//             .map((m, i) => (
//               <li key={i} style={{ margin: "0.5rem 0" }}>
//                 ➤ {m.text}
//               </li>
//             ))}
//         </ul>
//       </div>

//       {/* Chat window */}
//       <div
//         style={{
//           flex: 1,
//           display: "flex",
//           flexDirection: "column",
//           backgroundColor: "#fff",
//         }}
//       >
//         {/* Messages */}
//         <div
//           style={{
//             flex: 1,
//             padding: "1rem",
//             overflowY: "auto",
//           }}
//         >
//           {messages.map((m, i) => (
//             <div
//               key={i}
//               style={{
//                 display: "flex",
//                 justifyContent: m.sender === "user" ? "flex-end" : "flex-start",
//                 marginBottom: "1rem",
//               }}
//             >
//               <div
//                 style={{
//                   background: m.sender === "user" ? "#007bff" : "#eee",
//                   color: m.sender === "user" ? "#fff" : "#000",
//                   padding: "0.8rem 1rem",
//                   borderRadius: "10px",
//                   maxWidth: "60%",
//                 }}
//               >
//                 {m.text}
//               </div>
//             </div>
//           ))}
//           {loading && <p>Bot is typing...</p>}
//         </div>

//         {/* Input bar */}
//         <div
//           style={{
//             display: "flex",
//             padding: "1rem",
//             borderTop: "1px solid #ccc",
//           }}
//         >
//           <input
//             type="text"
//             value={question}
//             onChange={(e) => setQuestion(e.target.value)}
//             placeholder="Type your question..."
//             style={{
//               flex: 1,
//               padding: "0.7rem",
//               border: "1px solid #ccc",
//               borderRadius: "5px",
//             }}
//           />
//           <button
//             onClick={handleAsk}
//             style={{
//               padding: "0.7rem 1.2rem",
//               marginLeft: "0.5rem",
//               backgroundColor: "#007bff",
//               color: "#fff",
//               border: "none",
//               borderRadius: "5px",
//             }}
//           >
//             Ask
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

// import React, { useState } from "react";
// import axios from "axios";
// import ReactMarkdown from "react-markdown";
// import { Prism as SyntaxHighlighter } from "react-syntax-highlighter";
// import { oneDark } from "react-syntax-highlighter/dist/esm/styles/prism";

// function App() {
//   const [question, setQuestion] = useState("");
//   const [chatHistory, setChatHistory] = useState([]);
//   const [loading, setLoading] = useState(false);

//   const handleAsk = async () => {
//     if (!question) return;
//     setLoading(true);

//     try {
//       const response = await axios.post("http://127.0.0.1:8000/ask", { question });
//       const answer = response.data.answer;

//       setChatHistory((prev) => [
//         ...prev,
//         { question, answer }
//       ]);
//     } catch (err) {
//       console.error(err);
//       setChatHistory((prev) => [
//         ...prev,
//         { question, answer: "Error fetching answer from backend." }
//       ]);
//     }

//     setQuestion("");
//     setLoading(false);
//   };

//   // Copy button component
//   const CopyButton = ({ text }) => {
//     const [copied, setCopied] = useState(false);

//     const handleCopy = () => {
//       navigator.clipboard.writeText(text);
//       setCopied(true);
//       setTimeout(() => setCopied(false), 2000);
//     };

//     return (
//       <button
//         onClick={handleCopy}
//         style={{
//           position: "absolute",
//           top: "5px",
//           right: "5px",
//           background: copied ? "#4caf50" : "#333",
//           color: "white",
//           border: "none",
//           padding: "4px 8px",
//           borderRadius: "4px",
//           cursor: "pointer",
//           fontSize: "12px"
//         }}
//       >
//         {copied ? "Copied!" : "Copy"}
//       </button>
//     );
//   };

//   return (
//     <div style={{ display: "flex", height: "100vh", fontFamily: "Arial, sans-serif" }}>
//       {/* Left side – Chat history */}
//       <div style={{ width: "20%", borderRight: "1px solid #ddd", padding: "1rem", overflowY: "auto" }}>
//         <h3>History</h3>
//         {chatHistory.map((chat, idx) => (
//           <div key={idx} style={{ marginBottom: "1rem" }}>
//             <strong>Q:</strong> {chat.question}
//           </div>
//         ))}
//       </div>

//       {/* Right side – Chat window */}
//       <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
//         {/* Messages */}
//         <div style={{ flex: 1, padding: "1rem", overflowY: "auto" }}>
//           {chatHistory.map((chat, idx) => (
//             <div key={idx} style={{ marginBottom: "1.5rem" }}>
//               <p><strong>Q:</strong> {chat.question}</p>
//               <div
//                 style={{
//                   background: "#f4f4f4",
//                   padding: "0.75rem",
//                   borderRadius: "8px",
//                   position: "relative"
//                 }}
//               >
//                 <ReactMarkdown
//                   children={chat.answer.replace(/\n\s*\n/g, "\n")}
//                   components={{
//                     code({ node, inline, className, children, ...props }) {
//                       const match = /language-(\w+)/.exec(className || "");
//                       const codeText = String(children).replace(/\n$/, "");

//                       return !inline && match ? (
//                         <div style={{ position: "relative" }}>
//                           <CopyButton text={codeText} />
//                           <SyntaxHighlighter
//                             style={oneDark}
//                             language={match[1]}
//                             PreTag="div"
//                             {...props}
//                           >
//                             {codeText}
//                           </SyntaxHighlighter>
//                         </div>
//                       ) : (
//                         <code
//                           style={{
//                             background: "#eee",
//                             padding: "2px 4px",
//                             borderRadius: "4px"
//                           }}
//                           {...props}
//                         >
//                           {children}
//                         </code>
//                       );
//                     }
//                   }}
//                 />
//               </div>
//             </div>
//           ))}
//           {loading && <p>Loading...</p>}
//         </div>

//         {/* Input Bar at bottom */}
//         <div style={{ display: "flex", borderTop: "1px solid #ddd", padding: "1rem" }}>
//           <input
//             type="text"
//             value={question}
//             onChange={(e) => setQuestion(e.target.value)}
//             placeholder="Type your question..."
//             style={{ flex: 1, padding: "0.5rem", borderRadius: "8px", border: "1px solid #ccc" }}
//             onKeyDown={(e) => e.key === "Enter" && handleAsk()}
//           />
//           <button
//             onClick={handleAsk}
//             style={{
//               marginLeft: "1rem",
//               padding: "0.5rem 1rem",
//               borderRadius: "8px",
//               border: "none",
//               background: "#4CAF50",
//               color: "white",
//               cursor: "pointer"
//             }}
//           >
//             Ask
//           </button>
//         </div>
//       </div>
//     </div>
//   );
// }

// export default App;


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

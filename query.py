# query.py
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA

# -----------------------------
# 1️⃣ Setup embeddings
# -----------------------------
embedding_function = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)

# -----------------------------
# 2️⃣ Setup vector database
# -----------------------------
vectordb = Chroma(
    collection_name="my_collection",
    embedding_function=embedding_function,
    persist_directory="./chroma_db"
)

# -----------------------------
# 3️⃣ Setup LLM
# -----------------------------
llm = ChatOpenAI(
    model_name="gpt-4o-mini",
    temperature=0,
    openai_api_key="sk-"  # <-- Add your OpenAI API key
)

# -----------------------------
# 4️⃣ Setup Retrieval QA
# -----------------------------
qa = RetrievalQA.from_chain_type(
    llm=llm,
    retriever=vectordb.as_retriever(),
    chain_type="stuff"
)

# -----------------------------
# 5️⃣ Main loop
# -----------------------------
print("📘 Ask me anything about your subjects (type 'exit' to quit)\n")

while True:
    query = input("Your question: ")
    if query.lower() in ["exit", "quit"]:
        print("Bye!")
        break
    result = qa.invoke(query)  # using invoke to avoid deprecated .run()
    print("\nAnswer:", result, "\n")

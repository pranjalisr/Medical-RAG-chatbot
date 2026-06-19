from flask import Flask, render_template, jsonify, request, session
from src.helper import download_hugging_face_embeddings
from langchain_pinecone import PineconeVectorStore
from langchain_openai import ChatOpenAI
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
from src.prompt import system_prompt, contextualize_q_system_prompt
import os
import secrets

app = Flask(__name__)
app.secret_key = secrets.token_hex(32)  # Required for session-based chat history

load_dotenv()

PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')

os.environ["PINECONE_API_KEY"] = PINECONE_API_KEY

# ---------------------------------------------------------------------------
# Embeddings + Vector Store
# ---------------------------------------------------------------------------

embeddings = download_hugging_face_embeddings()

index_name = "medical-chatbot"

docsearch = PineconeVectorStore.from_existing_index(
    index_name=index_name,
    embedding=embeddings
)

retriever = docsearch.as_retriever(
    search_type="similarity",
    search_kwargs={"k": 5}  # Retrieve top 5 passages for richer context
)

# ---------------------------------------------------------------------------
# LLM
# ---------------------------------------------------------------------------

llm = ChatOpenAI(
    model="deepseek-chat",
    temperature=0.2,
    max_tokens=512,
    openai_api_key=os.environ.get("DEEPSEEK_API_KEY"),
    openai_api_base="https://api.deepseek.com/v1"
)

# ---------------------------------------------------------------------------
# History-aware retriever
# Reformulates follow-up questions into standalone queries before retrieval
# ---------------------------------------------------------------------------

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

history_aware_retriever = create_history_aware_retriever(
    llm, retriever, contextualize_q_prompt
)

# ---------------------------------------------------------------------------
# RAG chain with structured system prompt
# ---------------------------------------------------------------------------

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

question_answer_chain = create_stuff_documents_chain(llm, qa_prompt)
rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)

# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    session.setdefault("chat_history", [])
    return render_template('chat.html')


@app.route("/get", methods=["POST"])
def chat():
    msg = request.form.get("msg", "").strip()
    if not msg:
        return jsonify({"answer": "Please enter a question.", "sources": []})

    # Rebuild LangChain message objects from session history
    history = session.get("chat_history", [])
    lc_history = []
    for turn in history:
        lc_history.append(HumanMessage(content=turn["human"]))
        lc_history.append(AIMessage(content=turn["ai"]))

    response = rag_chain.invoke({
        "input": msg,
        "chat_history": lc_history
    })

    answer = response["answer"]

    # Extract source snippets for display in the UI
    sources = []
    for doc in response.get("context", []):
        snippet = doc.page_content[:200].replace("\n", " ") + "…"
        sources.append(snippet)

    # Save this turn to session history (keep last 10 turns)
    history.append({"human": msg, "ai": answer})
    session["chat_history"] = history[-10:]

    return jsonify({"answer": answer, "sources": sources})


@app.route("/reset", methods=["POST"])
def reset():
    session["chat_history"] = []
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)
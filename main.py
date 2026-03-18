import os
import re
import streamlit as st

from database import engine, SessionLocal
from models import Base, RagHistory
from crud import save_history

os.environ["TOKENIZERS_PARALLELISM"] = "false"

from pdf2image import convert_from_path
import pytesseract

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_ollama import OllamaLLM

from rank_bm25 import BM25Okapi


# ensure tables exist
Base.metadata.create_all(bind=engine)


# -------------------------------
# SIDEBAR HISTORY FUNCTION
# -------------------------------

def get_history():

    db = SessionLocal()

    history = db.query(RagHistory)\
        .order_by(RagHistory.id.desc())\
        .limit(10)\
        .all()

    db.close()

    return history


# -------------------------------
# STREAMLIT SIDEBAR
# -------------------------------

st.sidebar.title("💬 Yours chats")

history = get_history()

if history:

    for item in history:

        with st.sidebar.expander(item.question):

            st.write("Answer:")
            st.write(item.answer)

            st.write("Sources:", item.sources)


# -------------------------------
# LOAD EMBEDDINGS
# -------------------------------

@st.cache_resource
def load_embeddings():
    return HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-en"
    )

embeddings = load_embeddings()


# CLEAN OCR TEXT
def clean_text(text):
    text = text.replace("|", " ")
    text = re.sub(r'[^a-zA-Z0-9\s:/.-]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()


# OCR PDF
def extract_text_from_pdf(pdf_path):

    pages = convert_from_path(
        pdf_path,
        dpi=150
    )

    data = []

    for i, page in enumerate(pages):

        raw_text = pytesseract.image_to_string(
            page,
            lang="eng",
            config="--psm 6"
        )

        text = clean_text(raw_text)

        data.append({
            "text": text,
            "page": i + 1
        })

    return data


# CHUNKING
def layout_chunking(text, page):

    sections = re.split(r'\n\s*\d+\.\s+', text)

    records = []

    for sec in sections:

        sec = sec.strip()

        if len(sec) > 80:

            records.append({
                "content": sec,
                "page": page
            })

    return records


# CREATE RECORDS
def create_records(ocr_data):

    records = []

    for doc in ocr_data:

        page = doc["page"]
        text = doc["text"]

        chunks = layout_chunking(text, page)

        records.extend(chunks)

    return records


# VECTOR DATABASE
def build_vector_db(records):

    texts = [r["content"] for r in records]
    metadatas = [{"page": r["page"]} for r in records]

    db = Chroma.from_texts(
        texts=texts,
        embedding=embeddings,
        metadatas=metadatas,
        persist_directory="./chroma_db"
    )

    return db


# BM25 SEARCH
def build_bm25(records):

    corpus = [r["content"] for r in records]
    tokenized = [doc.split() for doc in corpus]

    bm25 = BM25Okapi(tokenized)

    return bm25


# HYBRID SEARCH
def hybrid_search(query, vector_db, bm25, records):

    vector_docs = vector_db.similarity_search(query, k=6)

    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)

    top_n = sorted(
        range(len(scores)),
        key=lambda i: scores[i],
        reverse=True
    )[:3]

    keyword_docs = [records[i] for i in top_n]

    return vector_docs, keyword_docs


# LLM
llm = OllamaLLM(
    model="llama3:latest",
    temperature=0
)


# PROMPT
prompt = PromptTemplate.from_template("""
### ROLE
You are a Legal Document Assistant.
Your job is to answer questions strictly using the provided document context.

### INSTRUCTIONS

1. Use ONLY the information present in the provided document context.
2. If the answer is clearly available in the context, provide a concise answer.
3. If the information is NOT present, respond exactly with:

Not enough information in the document.

4. Do NOT use external knowledge.
5. Do NOT guess or assume missing information.

### DOCUMENT CONTEXT
{context}

### USER QUESTION
{question}

### FINAL ANSWER
""")


parser = StrOutputParser()
chain = prompt | llm | parser


# -------------------------------
# STREAMLIT MAIN UI
# -------------------------------

st.title("📄 Legal Document RAG Assistant")
st.write("Upload a PDF and ask questions about it.")

uploaded_file = st.file_uploader("Upload your PDF", type="pdf")


# PROCESS PDF
if uploaded_file:

    with st.spinner("Processing PDF..."):

        pdf_path = "temp.pdf"

        with open(pdf_path, "wb") as f:
            f.write(uploaded_file.read())

        ocr_data = extract_text_from_pdf(pdf_path)

        records = create_records(ocr_data)

        vector_db = build_vector_db(records)

        bm25 = build_bm25(records)

    st.success("PDF processed successfully!")


    # QUESTION FORM
    with st.form("question_form"):

        question = st.text_input("Enter your question")

        submit = st.form_submit_button("🔍 Get Answer")


    if submit and question:

        with st.spinner("Generating answer..."):

            vector_docs, keyword_docs = hybrid_search(
                question,
                vector_db,
                bm25,
                records
            )

            context_parts = []
            pages = []

            for d in vector_docs:
                context_parts.append(d.page_content)
                pages.append(d.metadata["page"])

            for d in keyword_docs:
                context_parts.append(d["content"])
                pages.append(d["page"])

            context = "\n\n".join(context_parts)

            pages = sorted(set(pages))

            answer = chain.invoke({
                "context": context,
                "question": question
            })

            # SAVE TO MYSQL
            document_name = uploaded_file.name

            save_history(
                question,
                answer,
                str(pages),
                document_name
            )

        st.subheader("Answer")
        st.write(answer)

        if "Not enough information" in answer:
            st.write("Sources: None")

        else:
            st.subheader("Sources")

            for p in pages:
                st.write(f"📄 Page {p}")
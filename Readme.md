# 📄 **Legal Document RAG Assistant**

A Streamlit-based **Retrieval-Augmented Generation (RAG)** application that lets users upload PDFs and ask questions strictly based on their content.

👉 **No hallucinations. No external data. 100% document-grounded answers.**

---

## 🚀 **Key Features**

* 📥 **Upload PDF Documents**
* 🔍 **OCR Support** for scanned PDFs *(Tesseract)*
* 🧠 **Hybrid Search System**

  * **Semantic Search** → Chroma + Embeddings
  * **Keyword Search** → BM25
* 🤖 **Local LLM (Ollama)** → *No API cost*
* 📑 **Accurate Page Number Tracking**
* 💬 **Chat History Sidebar**
* 💾 **Database Storage** *(MySQL / SQLite)* for Q&A + sources

---

## 🧱 **Tech Stack**

| Component      | Technology                        |
| -------------- | --------------------------------- |
| Frontend       | Streamlit                         |
| LLM            | Ollama *(llama3)*                 |
| Embeddings     | HuggingFace *(BAAI/bge-small-en)* |
| Vector DB      | Chroma                            |
| Keyword Search | BM25                              |
| OCR            | Tesseract + pdf2image             |
| Database       | SQLAlchemy *(MySQL / SQLite)*     |

---

## 📂 **Project Structure**

```bash
.
├── main.py              # Main Streamlit app
├── database.py          # DB connection
├── models.py            # ORM models
├── crud.py              # DB operations
├── requirements.txt
├── chroma_db/           # Vector DB storage
└── temp.pdf             # Temporary uploaded file
```

---

## ⚙️ **Installation Steps**

### 1️⃣ Clone Repository

```bash
git clone https://github.com/your-username/rag-app.git
cd rag-app
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate   # Mac/Linux
venv\Scripts\activate      # Windows
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🧠 **Install Ollama (Local LLM)**

👉 https://ollama.com

```bash
ollama pull llama3
```

---

## 🔤 **Install Tesseract OCR**

### Mac

```bash
brew install tesseract
```

### Ubuntu

```bash
sudo apt install tesseract-ocr
```

### Windows

* Download: https://github.com/tesseract-ocr/tesseract
* Add to **PATH**

---

## ▶️ **Run the Application**

```bash
streamlit run main.py
```

👉 Open in browser:
**http://localhost:8502**

---

## 🔄 **How It Works**

1. 📥 **Upload PDF**
2. 🔍 **OCR Processing**

   * PDF → Images
   * Text extraction via Tesseract
3. ✂️ **Chunking**

   * Splits into meaningful sections
4. 📊 **Indexing**

   * Embeddings → Chroma
   * Tokens → BM25
5. 🔎 **Hybrid Retrieval**

   * Combines semantic + keyword search
6. 🤖 **Answer Generation**

   * Uses only retrieved context
7. 📑 **Source Tracking**

   * Returns exact page numbers
8. 💾 **History Storage**

   * Saves Q&A in database

---

## 📌 **Important Highlights**

* ✅ Runs completely **offline** after setup
* ✅ **Zero API cost** *(local LLM)*
* ✅ Strict prompt → **prevents hallucination**
* ✅ Accurate **page-level source attribution**

👉 If answer not found:

```text
"Not enough information in the document."
```

---

## 🧾 **Use Cases**

* 📄 Legal document analysis
* 📑 Contract review
* 📘 Policy Q&A
* ⚖️ Compliance verification

---

## 🛠️ **Future Improvements**

* Multi-document support
* Layout-aware chunking
* Highlight answers inside PDF
* Better UI/UX
* Streaming responses

---

## 🤝 **Contributing**

Pull requests are welcome.
For major changes, please open an issue first.

---

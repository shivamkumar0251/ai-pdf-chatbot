# AI PDF Chatbot: Technical Project Documentation

This document provides a comprehensive technical overview of the AI PDF Chatbot project. It is designed to explain the internal working, logic flow, and technology choices to clients or technical interviewers.

---

## 1. Project Overview
This project is an **AI-powered Question Analyser & Chatbot** based on **RAG (Retrieval-Augmented Generation)** architecture. It allows users to upload PDF documents and ask questions based *specifically* on the content of those documents.

Key Features:
- **PDF Ingestion**: Extracts text from PDF files.
- **Semantic Search**: Understands the *meaning* of the question, not just keywords.
- **Generative AI**: Uses OpenAI's GPT models to generate human-like answers based on the retrieved context.

---

## 2. Technology Stack & Justification
*Why we chose these specific technologies and versions:*

### **Backend Framework: FastAPI**
*   **Why used?**: FastAPI is modern, high-performance, and built on Python 3.6+ standard type hints.
*   **Advantage over Flask/Django**: It natively supports **Asynchronous (async/await)** operations. Since our app deals with I/O bound tasks (like calling OpenAI APIs or reading files), `async` allows the server to handle multiple requests without freezing. It also auto-generates API documentation (Swagger UI).

### **PDF Processing: pdfplumber**
*   **Why used?**: While libraries like `PyPDF2` exist, `pdfplumber` is significantly better at extracting text accurately, especially from complex layouts or tables. It provides a reliable stream of text which is crucial for the AI to understand the context.

### **Vector Database: FAISS (Facebook AI Similarity Search)**
*   **Why used?**: FAISS is the industry standard for efficient similarity search and clustering of dense vectors.
*   **Why `faiss-cpu`?**: For this scale of application (running locally or on standard servers), the CPU version is highly optimized and avoids the complexity/dependency of CUDA (GPU) drivers. It allows for extremely fast similarity lookups (Nearest Neighbor Search) in memory.

### **AI Models: OpenAI**
*   **LLM (`gpt-4o-mini`)**: We use `gpt-4o-mini` because it offers an excellent balance between **cost, speed, and intelligence**. It is cheaper and faster than GPT-4, but capable enough for RAG tasks.
*   **Embeddings (`text-embedding-3-small`)**: This is OpenAI's latest efficient embedding model. It converts text into 1536-dimensional vectors, capturing deep semantic meaning at a low cost.

### **Server: Uvicorn**
*   **Why used?**: A lightning-fast ASGI server implementation, needed to run FastAPI applications (since FastAPI doesn't include a server itself).

---

## 3. Codebase Structure & Logic Flow
Here is the breakdown of the "Brain" of the application:

### **A. Entry Point (`main.py`)**
This is the controller. It connects the outside world (API Requests) to internal logic.
*   **`/upload-pdf`**:
    1.  Receives the file stream.
    2.  **Saves to Disk**: Writes the binary content to `data/uploads/` to ensure we have a backup of the source file.
    3.  Triggers the **Ingestion Pipeline**: Extract -> Split -> Embed -> Store.
*   **`/ask`**:
    1.  Receives the user's question string.
    2.  Calls the RAG module to generate an answer.

### **B. The Reader (`pdf_loader.py`)**
*   **Logic**: Opens the PDF file path using `pdfplumber`. Iterates through every page, extracting text strings and appending them to create one large document body.

### **C. The Cutter (`text_splitter.py`)**
*   **Problem**: AI models have a token limit (context window). We cannot feed an entire book at once.
*   **Solution**: We slice the text into **Chunks** (e.g., 500 characters).
*   **Overlap Logic**: We keep an `overlap` (e.g., 50 chars). If a sentence gets cut in half at the end of Chunk A, the overlap ensures the beginning of Chunk B contains that missing half. This prevents context loss.

### **D. The Translator (`embeddings.py`)**
*   **Logic**: Converts human text into "Machine Numbers" (Embeddings).
*   **Process**: Takes a list of text chunks -> Sends to OpenAI API -> Returns a list of Vectors (lists of floating-point numbers).

### **E. The Memory (`vector_store.py`)**
*   **Data Structure**: Uses a FAISS Index (`IndexFlatL2`).
*   **Logic**:
    *   **Store**: Adds the vectors to the index for mathematical searching. It also maintains a parallel list `stored_chunks` to keep the actual text content corresponding to each vector.
    *   **Search**: When a query vector comes in, it calculates the **Euclidean Distance (L2)** to find vectors that are "closest" (most similar in meaning) to the query.

### **F. The Brain (`rag.py`)**
*   **Workflow**:
    1.  **Embed Query**: Converts the user's question into a vector.
    2.  **Retrieve**: Asks `vector_store` for the top 3 most relevant chunks.
    3.  **Prompt Engineering**: Constructs a prompt that strictly instructs the AI: *"Using ONLY the following context, answer the question"*. This reduces hallucinations (AI making things up).
    4.  **Generate**: Sends the prompt to GPT-4o-mini and returns the text response.

---

## 4. End-to-End Workbook (How PDF is Saved & Processed)

1.  **User Uploads**: User sends a POST request with a PDF file.
2.  **File Writing**: The server opens a file handle in binary write mode (`wb`) and saves the exact bytes to the `data/uploads` directory. This persists the file locally.
3.  **Processing Trigger**: Immediately after saving, the server reads that file from the disk.
4.  **Vectorization**: The text flows through the pipeline (Loader -> Splitter -> Embedding).
5.  **Indexing**: The mathematical representation of the PDF is loaded into RAM (FAISS Index).
6.  **Ready State**: The API returns "PDF processed successfully". The system is now ready to answer questions about that specific PDF.

---

## 5. Summary for Interviews
*"This project is a scalable, async-enabled RAG application built with FastAPI. It solves the problem of querying large documents by leveraging vector similarity search (FAISS) and LLMs (OpenAI). The modular creation of loaders, splitters, and vector stores ensures that we can easily swap out components (e.g., changing the database to Pinecone or the model to Llama) without rewriting the entire application."*

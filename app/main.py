from fastapi import FastAPI, UploadFile, File, HTTPException
from app.pdf_loader import extract_text
from app.text_splitter import chunk_text
from app.embeddings import get_embeddings
from app.vector_store import store_vectors, get_all_chunks
from app.rag import answer_question

import os

app = FastAPI()
UPLOAD_DIR = "data/uploads"

@app.post("/upload-pdf")
async def upload_pdf(file: UploadFile = File(...)):
    file_path = f"{UPLOAD_DIR}/{file.filename}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(await file.read())

    text = extract_text(file_path)
    chunks = chunk_text(text)
    try:
        embeddings = get_embeddings(chunks)
        store_vectors(embeddings, chunks)
    except Exception as e:
        if "insufficient_quota" in str(e):
            raise HTTPException(status_code=429, detail="OpenAI quota exceeded. Please check your OpenAI account and billing details.")
        else:
            raise HTTPException(status_code=500, detail=f"An error occurred while processing the PDF: {str(e)}")

    return {"message": "PDF processed and indexed successfully"}

@app.post("/ask")
async def ask(question: str):
    answer = answer_question(question)
    return {"answer": answer}

@app.get("/chunks")
def get_chunks():
    chunks = get_all_chunks()
    return {
        "total_chunks": len(chunks),
        "chunks": chunks
    }
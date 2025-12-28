# AI PDF Chatbot (RAG)

## Problem
Businesses store important information in PDFs that are hard to search and analyze.

## Solution
An AI-powered chatbot that allows users to upload PDF documents and ask questions.
The system uses Retrieval Augmented Generation (RAG) to provide accurate answers
directly from document content.

## Features
- Upload PDF documents
- Automatic text extraction and indexing
- Ask natural language questions
- Accurate answers based only on documents
- Simple REST APIs

## Tech Stack
- FastAPI
- Python
- Retrieval Augmented Generation (RAG)
- FAISS Vector Database
- OpenAI Embeddings

## How to Run

```bash
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload

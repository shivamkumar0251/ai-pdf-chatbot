from app.embeddings import get_embeddings
from app.vector_store import search_vectors
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def answer_question(question: str):
    question_embedding = get_embeddings([question])[0]
    relevant_chunks = search_vectors(question_embedding)

    context = "\n".join(relevant_chunks)

    prompt = f"""
Use only the following context to answer the question.
If the answer is not in the context, say "Not found in document".

Context:
{context}

Question:
{question}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content

import faiss
import numpy as np

index = faiss.IndexFlatL2(1536)
stored_chunks = []

def store_vectors(embeddings, chunks):
    global stored_chunks
    vectors = np.array(embeddings).astype("float32")
    index.add(vectors)
    stored_chunks.extend(chunks)

def search_vectors(query_embedding, k=3):
    query_vector = np.array([query_embedding]).astype("float32")
    distances, indices = index.search(query_vector, k)
    return [stored_chunks[i] for i in indices[0]]

def get_all_chunks():
    return stored_chunks

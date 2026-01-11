from sentence_transformers import SentenceTransformer
import faiss
import os

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

index = None
documents = []


def load_faqs():
    global index, documents

    file_path = os.path.join("data", "faqs.txt")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    documents = [chunk.strip() for chunk in text.split("\n\n") if chunk.strip()]

    embeddings = embedding_model.encode(documents)

    dimension = embeddings.shape[1]
    index = faiss.IndexFlatL2(dimension)
    index.add(embeddings)


def search_faqs(query: str, top_k: int = 2) -> str:
    if index is None:
        load_faqs()

    query_embedding = embedding_model.encode([query])
    distances, indices = index.search(query_embedding, top_k)

    results = [documents[i] for i in indices[0]]

    return "\n".join(results)

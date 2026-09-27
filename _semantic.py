"""Semantic retrieval with embeddings - SAME fit()/search() interface as TfidfIndex,
so the rest of the RAG code doesn't change; we just swap the retriever.

Why it helps: embeddings map MEANING to nearby vectors, so "my app keeps dying and
restarting" can match an "OOMKilled" runbook even with no shared words - something plain
keyword search cannot do (see 02_keyword_vs_semantic.py).

Needs one extra install. It downloads a small model (~90MB) the FIRST time, then runs
offline, locally, and free:

    pip install sentence-transformers

'all-MiniLM-L6-v2' is small and CPU-friendly. For a large corpus you would store these
vectors in a vector database (e.g. Chroma) instead of recomputing them every run.
"""
MODEL_NAME = "all-MiniLM-L6-v2"


class SemanticIndex:
    def __init__(self, model_name=MODEL_NAME):
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as e:
            raise ImportError(
                "SemanticIndex needs sentence-transformers -> pip install sentence-transformers"
            ) from e
        self.model = SentenceTransformer(model_name)
        self.chunks, self.embs = [], None

    def fit(self, chunks):
        self.chunks = chunks
        texts = [c["text"] for c in chunks]
        # normalize so cosine similarity is just a dot product
        self.embs = self.model.encode(texts, normalize_embeddings=True, convert_to_numpy=True)
        return self

    def search(self, query, k=3):
        """Return [(cosine_score, chunk)] for the top-k chunks, best first."""
        q = self.model.encode([query], normalize_embeddings=True, convert_to_numpy=True)[0]
        sims = self.embs @ q                       # vectors are normalized -> dot == cosine
        order = sims.argsort()[::-1][:k]
        return [(float(sims[i]), self.chunks[i]) for i in order]

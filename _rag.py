"""RAG retrieval core - pure standard library, no external services, no API key.

This is the R in RAG: load runbooks -> chunk by section -> score chunks against a
question with TF-IDF + cosine similarity -> return the best sections. Keyword retrieval
runs anywhere with zero setup and is easy to read; Episode 10 upgrades this to vector
embeddings (semantic search) for questions that don't share words with the docs.
"""
import os
import re
import math

STOP = set(
    "the a an of to and or is are be was were in on at for with your you it its this that "
    "from as by we our if then when what how do does can will not no".split()
)


def tokenize(s):
    return [t for t in re.findall(r"[a-z0-9]+", s.lower()) if len(t) >= 2 and t not in STOP]


def load_runbooks(folder="runbooks"):
    """Return [(filename, text)] for every .md file in the folder."""
    out = []
    for name in sorted(os.listdir(folder)):
        if name.endswith(".md"):
            with open(os.path.join(folder, name), encoding="utf-8") as f:
                out.append((name, f.read()))
    return out


def chunk_markdown(text, source):
    """Split one runbook into chunks, one per '## ' section. Each chunk carries its
    source file + section heading so we can cite exactly where an answer came from."""
    title = source
    sections, head, body = [], None, []
    for ln in text.splitlines():
        if ln.startswith("# ") and not ln.startswith("## "):
            title = ln[2:].strip()
        elif ln.startswith("## "):
            if head or body:
                sections.append((head, body))
            head, body = ln[3:].strip(), []
        else:
            body.append(ln)
    if head or body:
        sections.append((head, body))
    chunks = []
    for head, body in sections:
        body_txt = "\n".join(body).strip()
        if head is None and not body_txt:
            continue  # skip the empty preamble between the title and the first '## ' section
        section = head or title
        # Fold the doc title into every chunk so title keywords help each section match,
        # and so a chunk read on its own still says which runbook it is from.
        heading = section if section == title else f"{title} :: {section}"
        txt = (heading + "\n" + body_txt).strip()
        if txt:
            chunks.append({"source": source, "title": title, "section": section, "text": txt})
    return chunks


def build_chunks(folder="runbooks"):
    chunks = []
    for name, text in load_runbooks(folder):
        chunks.extend(chunk_markdown(text, name))
    return chunks


def chunk_with_overlap(text, source, size=60, overlap=15):
    """Split each section further into overlapping word-windows of ~`size` words.

    Why overlap: a step or sentence that straddles a window boundary would be split in
    half and become un-retrievable. Overlapping the windows keeps it whole in at least
    one of them. Short sections (<= size) are left as a single chunk."""
    out = []
    for c in chunk_markdown(text, source):
        words = c["text"].split()
        if len(words) <= size:
            out.append(c)
            continue
        step = max(1, size - overlap)
        for w in range(0, len(words), step):
            piece = " ".join(words[w:w + size])
            if piece.strip():
                out.append({**c, "text": piece})
            if w + size >= len(words):
                break
    return out


def build_overlap(folder="runbooks", size=60, overlap=15):
    chunks = []
    for name, text in load_runbooks(folder):
        chunks.extend(chunk_with_overlap(text, name, size, overlap))
    return chunks


class TfidfIndex:
    """Tiny TF-IDF cosine index over the chunks. Deterministic and transparent."""

    def __init__(self):
        self.chunks, self.vecs, self.idf = [], [], {}

    def fit(self, chunks):
        self.chunks = chunks
        docs = [tokenize(c["text"]) for c in chunks]
        df = {}
        for toks in docs:
            for t in set(toks):
                df[t] = df.get(t, 0) + 1
        n = len(docs)
        self.idf = {t: math.log((n + 1) / (d + 1)) + 1 for t, d in df.items()}
        self.vecs = [self._vec(toks) for toks in docs]
        return self

    def _vec(self, toks):
        if not toks:
            return {}
        tf = {}
        for t in toks:
            tf[t] = tf.get(t, 0) + 1
        return {t: (f / len(toks)) * self.idf.get(t, 0.0) for t, f in tf.items()}

    @staticmethod
    def _cos(a, b):
        if not a or not b:
            return 0.0
        num = sum(a[t] * b.get(t, 0.0) for t in a)
        na = math.sqrt(sum(x * x for x in a.values()))
        nb = math.sqrt(sum(x * x for x in b.values()))
        return num / (na * nb) if na and nb else 0.0

    def search(self, query, k=3):
        """Return [(score, chunk)] for the top-k chunks, best first."""
        q = self._vec(tokenize(query))
        scored = [(self._cos(q, v), c) for v, c in zip(self.vecs, self.chunks)]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:k]

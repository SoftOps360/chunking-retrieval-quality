"""ask-runbook (v2) - the Episode 9 tool, upgraded with semantic retrieval.

Uses embeddings (SemanticIndex) when sentence-transformers is installed, and falls back to
the zero-install keyword index otherwise - printing which one it used. Same grounding,
citations, and honest "No runbook covers this" as before; just a better retriever.

  python ask-runbook.py "my app keeps dying and restarting"
  echo "go back to the previous version after a bad release" | python ask-runbook.py
"""
import sys
from _rag import build_chunks
from _llm import ask

# Different retrievers use different score scales, so each gets its own threshold.
MIN_SCORE_SEM = 0.30   # cosine similarity (embeddings) - a starting point; tune for your corpus
MIN_SCORE_KW = 0.05    # TF-IDF (keyword fallback)

SYSTEM = (
    "You are an on-call assistant. Answer ONLY using the CONTEXT below, which comes from "
    "the team's runbooks. Do not use outside knowledge. If the context does not contain the "
    "answer, reply exactly: 'No runbook covers this.' Keep it short and practical, and cite "
    "the source file in square brackets like [oom-killed.md] after each claim."
)


def get_index():
    chunks = build_chunks("runbooks")
    try:
        from _semantic import SemanticIndex
        return SemanticIndex().fit(chunks), MIN_SCORE_SEM, "semantic (embeddings)"
    except ImportError:
        from _rag import TfidfIndex
        return TfidfIndex().fit(chunks), MIN_SCORE_KW, "keyword (TF-IDF fallback)"


def main():
    question = " ".join(sys.argv[1:]).strip() or sys.stdin.read().strip()
    if not question:
        print('Usage: python ask-runbook.py "your ops question"')
        return

    index, min_score, kind = get_index()
    print(f"[retriever: {kind}]")
    hits = index.search(question, 3)

    print(f"\nQ: {question}")
    if not hits or hits[0][0] < min_score:
        print("\nNo runbook covers this. (Nothing relevant retrieved - add a runbook for it.)")
        return

    context = "\n\n".join(f"[{c['source']} :: {c['section']}]\n{c['text']}" for _, c in hits)
    reply = ask(f"CONTEXT:\n{context}\n\nQUESTION: {question}", system=SYSTEM)

    print("\n" + reply)
    print("\nSources retrieved:")
    for score, c in hits:
        print(f"  {score:.3f}  [{c['source']} :: {c['section']}]")
    print("\n(Verify against the runbook before acting - the AI only summarizes what it retrieved.)")


if __name__ == "__main__":
    main()

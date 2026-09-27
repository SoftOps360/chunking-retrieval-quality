"""Step 2 - WHY embeddings. The same questions, phrased the way a tired on-call engineer
actually types them - different WORDS from the runbook, same MEANING.

Keyword search (Episode 9's TF-IDF) needs shared words, so it stumbles here. This is not a
made-up example: run it and read the 'WRONG' lines. Embeddings match by meaning, so they
recover these. The keyword half needs no install; the semantic half needs sentence-transformers
(see _semantic.py) - if it isn't installed we say so instead of crashing.
"""
from _rag import build_chunks, TfidfIndex

# These three are VERIFIED to fail on keyword search (wrong runbook) - the words differ too
# much from the docs. That's the point: run it and read the 'WRONG' lines yourself.
HARD = [
    ("my app keeps dying and restarting for no reason", "oom-killed.md"),
    ("shipping the update took payments down, restore what worked before", "rollback-payment-service.md"),
    ("customers cannot pay since we shipped the new build", "rollback-payment-service.md"),
]

chunks = build_chunks("runbooks")
kw = TfidfIndex().fit(chunks)

sem = None
try:
    from _semantic import SemanticIndex
    print("Loading the embedding model (first run downloads ~90MB)...\n")
    sem = SemanticIndex().fit(chunks)
except ImportError as e:
    print(f"(semantic index unavailable: {e})\n")

for q, want in HARD:
    print(f"Q: {q}\n   expected -> {want}")
    ks, kc = kw.search(q, 1)[0]
    print(f"   keyword : {ks:.3f}  {kc['source']:32s} {'OK' if kc['source'] == want else 'WRONG'}")
    if sem:
        ss, sc = sem.search(q, 1)[0]
        print(f"   semantic: {ss:.3f}  {sc['source']:32s} {'OK' if sc['source'] == want else 'WRONG'}")
    else:
        print("   semantic: (install sentence-transformers to compare)")
    print()

print("Takeaway: keyword retrieval is fast and zero-setup, but it only matches WORDS. "
      "When the words differ, embeddings win. Many production systems use BOTH (hybrid).")

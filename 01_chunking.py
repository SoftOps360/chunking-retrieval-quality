"""Step 1 - chunking quality. No AI. Retrieval can only be as good as your chunks.

Too big  -> one chunk mixes many topics, so the score is diluted and citations are vague.
Too small -> a step gets split from its context and loses meaning.
A good default for ops docs: chunk by section, and split any long section into OVERLAPPING
windows so nothing important falls on a boundary.
"""
from _rag import load_runbooks, chunk_markdown, chunk_with_overlap

text = dict(load_runbooks("runbooks"))["nginx-502-bad-gateway.md"]

by_section = chunk_markdown(text, "nginx-502-bad-gateway.md")
print(f"By section: {len(by_section)} chunks")
for c in by_section:
    print(f"   [{c['section']}]  {len(c['text'].split())} words")

overlapped = chunk_with_overlap(text, "nginx-502-bad-gateway.md", size=40, overlap=10)
print(f"\nWith overlap (size=40, overlap=10): {len(overlapped)} chunks")
for c in overlapped:
    print(f"   [{c['section']}]  {len(c['text'].split())} words")

print("\nOverlap only splits the LONG sections; short ones stay whole. "
      "The 10-word overlap keeps a step that straddles a boundary retrievable from either side.")

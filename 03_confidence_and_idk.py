"""Step 3 - a trustworthy "I don't know". No AI here either.

A RAG system that ALWAYS answers is dangerous: ask it something you have no runbook for and
it will still produce a confident, wrong procedure. The fix is a gate on the top retrieval
score. This shows how to CHOOSE that threshold - look at where in-domain scores land vs
out-of-domain, and put the line in the gap.
"""
from _rag import build_chunks, TfidfIndex

kw = TfidfIndex().fit(build_chunks("runbooks"))


def top(q):
    return kw.search(q, 1)[0][0]


in_domain = ["nginx 502 from upstream", "disk full no space left", "rollback the payment service",
             "database connection pool exhausted"]
out_domain = ["what is the capital of france", "best pizza near me", "how do i center a div"]

print("In-domain questions (a runbook exists -> scores should be clearly above 0):")
for q in in_domain:
    print(f"   {top(q):.3f}  {q}")

print("\nOut-of-domain questions (no runbook -> scores should be near 0):")
for q in out_domain:
    print(f"   {top(q):.3f}  {q}")

THRESHOLD = 0.05
print(f"\nThere's a clear gap, so a threshold of {THRESHOLD} separates them:")
print("   top score >= threshold  -> answer (grounded + cited)")
print("   top score <  threshold  -> 'No runbook covers this.'  (don't call the LLM at all)")
print("\nTune the threshold for YOUR corpus, and note the semantic index uses a different "
      "scale (cosine), so it needs its own threshold - measure, don't guess.")

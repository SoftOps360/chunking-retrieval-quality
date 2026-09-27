# Episode 10 — Chunking & Retrieval Quality

Episode 9 built a working RAG tool with keyword search. This episode makes it *trustworthy*.
In RAG, **retrieval quality is the ceiling** — the LLM can only answer from what you hand it.
So we fix the three things that decide retrieval quality: **how you chunk**, **how you
match** (keyword vs embeddings), and **when you refuse**.

## 1. Chunking — the boring thing that decides everything

- **Too big:** one chunk mixes many topics, dilutes the score, and gives vague citations.
- **Too small:** a step gets cut off from its context and loses meaning.
- **Good default for ops docs:** chunk by section, then split any *long* section into
  **overlapping windows** so a step that straddles a boundary stays whole in at least one chunk.

`01_chunking.py` shows section-chunking vs overlap on a real runbook (no AI, no key).

## 2. Keyword vs embeddings — why meaning beats words

Keyword search (Episode 9's TF-IDF) only matches **shared words**. Watch it fail on questions
phrased the way a tired on-call engineer actually types them — these are **verified** failures,
not staged:

| Question | Right runbook | Keyword picks |
|----------|---------------|---------------|
| "my app keeps dying and restarting for no reason" | `oom-killed.md` | ❌ `nginx-502` |
| "shipping the update took payments down, restore what worked before" | `rollback-payment-service.md` | ❌ `nginx-502` |
| "customers cannot pay since we shipped the new build" | `rollback-payment-service.md` | ❌ `ssl-cert-expiry` |

**Embeddings** map *meaning* to nearby vectors, so "keeps dying and restarting" lands near
"OOMKilled / restarts in a loop" even with no shared words. `02_keyword_vs_semantic.py` runs
both retrievers side by side — run it and read the difference for yourself.

> Keyword isn't useless — it's fast and zero-setup, and many production systems use **both**
> (hybrid retrieval). Embeddings win specifically when the words differ but the meaning matches.

## 3. A trustworthy "I don't know"

A RAG system that *always* answers will confidently invent a procedure for something you have
no runbook for. `03_confidence_and_idk.py` shows how to pick the refuse-threshold: in-domain
questions score clearly above zero, out-of-domain score ~0, so you put the line in the gap.

## The semantic retriever needs one install

The keyword scripts (`01`, `03`, and the keyword half of `02`) run with **zero extra setup**.
The embeddings retriever (`_semantic.py`) needs:

```bash
pip install sentence-transformers
```

It downloads a small model (`all-MiniLM-L6-v2`, ~90MB) the **first** time, then runs
**offline, locally, and free**. No API and no key are needed for embeddings — only the final
*answer* step calls the LLM. For a large corpus you'd store these vectors in a **vector
database (e.g. Chroma)** instead of recomputing them each run; the retrieval idea is identical.

## Files

| File | What it shows | Needs |
|------|---------------|-------|
| `_rag.py` | Chunking (`chunk_markdown`, `chunk_with_overlap`) + `TfidfIndex` (keyword). | stdlib |
| `_semantic.py` | `SemanticIndex` — embeddings, **same `search()` interface** as the keyword index. | sentence-transformers |
| `_llm.py` | Shared client (`ask`) → Groq's free endpoint. | openai |
| `01_chunking.py` | Section chunks vs overlapping windows. | — |
| `02_keyword_vs_semantic.py` | The verified keyword failures, keyword vs semantic side by side. | semantic optional |
| `03_confidence_and_idk.py` | Choosing the "I don't know" threshold from real scores. | — |
| `ask-runbook.py` | Upgraded tool: semantic retrieval if installed, keyword fallback otherwise. | — |
| `runbooks/` | The same six runbooks as Episode 9 (same corpus, better retriever). | — |

## Setup & run

```bash
pip install -r requirements.txt          # openai, dotenv, sentence-transformers
cp .env.example .env                      # paste your free Groq key (Windows: copy)

python 01_chunking.py                     # no key, no embeddings
python 02_keyword_vs_semantic.py          # keyword works with no install; semantic needs the package
python 03_confidence_and_idk.py           # no key, no embeddings
python ask-runbook.py "my app keeps dying and restarting"
```

## Honesty & limits (please keep these in the video)

- **Retrieval quality is the ceiling** — if an answer is wrong, look at the retrieved sources
  first. Usually the fix is chunking or retrieval, not the prompt.
- **Embeddings aren't magic.** They can still miss; the semantic threshold needs tuning per
  corpus (cosine scores sit on a different scale than TF-IDF — measure, don't guess).
- **Same interface, swapped retriever.** `SemanticIndex` and `TfidfIndex` expose the same
  `fit()`/`search()`, so nothing else in the RAG code changes — that's the point.
- **Grounded + cited + refuses** — all the Episode 9 safety still holds; a better retriever
  doesn't remove the need to verify against the runbook before acting.
- Model results depend on the embedding model and version; `all-MiniLM-L6-v2` is a solid,
  small default, not the only choice.

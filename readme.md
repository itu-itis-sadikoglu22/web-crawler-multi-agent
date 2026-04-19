# Multi-Agent Web Crawler Project

This project is a single-machine web crawler and search tool built for a take-home systems assignment. It starts from a given origin URL, crawls pages up to a specified depth, stores the discovered content locally, and allows searching across indexed pages.

The project was developed using a multi-agent AI workflow. Different agents were assigned to architecture, crawling, storage, search, and review responsibilities during the development process, while the final implementation decisions were made by the human developer.

## What the system does

The system exposes two main capabilities:

### 1. Index

Starts a crawl from a given origin URL up to depth `k`.

Example:
- depth `0`: the origin page
- depth `1`: pages linked directly from the origin
- depth `2`: pages linked from those pages

During indexing, the system:
- normalizes URLs
- avoids crawling the same page twice within the same crawl job
- extracts links and page text
- stores pages in a local SQLite database
- updates a simple inverted index for search

### 2. Search

Searches indexed content and returns results in this format:

`(relevant_url, origin_url, depth)`

Where:
- `relevant_url` is the matched page
- `origin_url` is the crawl origin from which the page was discovered
- `depth` is the number of hops from that origin
 
 Search can also be run while indexing is active. In this implementation, pages are written to SQLite and added to the inverted index incrementally as they are processed. Because search reads directly from the same local database, a separate CLI invocation can return newly discovered results without waiting for the full crawl to complete.
## Multi-agent development workflow

This project was created using a structured multi-agent workflow during development.

The following agents were defined:
- Architect Agent
- Crawler Agent
- Search Agent
- Storage Agent
- Reviewer Agent

Each agent focused on a specific problem area and produced recommendations or design guidance. The final implementation was reviewed and selected by the human developer.

More details are included in:
- `multi_agent_workflow.md`
- `/agents/*.md`

## Design overview

The system is divided into the following parts:

- `crawler.py` handles crawl execution, queueing, workers, depth control, and duplicate prevention
- `fetcher.py` downloads HTML pages using Python standard library tools
- `parser.py` extracts links and visible text from HTML
- `storage.py` manages SQLite persistence
- `search.py` performs keyword search over the local inverted index
- `cli.py` provides a command-line interface for indexing, searching, and status inspection

## Back pressure

To keep the crawler controlled on a single machine, the system includes:
- a bounded in-memory queue
- a fixed worker count
- fetch timeouts
- controlled link scheduling

This prevents unbounded work generation and helps the system remain stable during crawling.

## Running the project

### Create a virtual environment

On Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
python -m app.main index https://example.com 1 --watch
python -m app.main search example
python -m app.main status

EXAMPLE OUTPT
1. relevant_url: https://example.com/
   origin_url  : https://example.com/
   depth       : 0


PROJECT STRUCTURE
web-crawler-multi-agent/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── cli.py
│   ├── crawler.py
│   ├── fetcher.py
│   ├── parser.py
│   ├── search.py
│   ├── storage.py
│   └── utils.py
├── agents/
│   ├── architect_agent.md
│   ├── crawler_agent.md
│   ├── search_agent.md
│   ├── storage_agent.md
│   └── reviewer_agent.md
├── data/
├── tests/
├── product_prd.md
├── readme.md
├── recommendation.md
├── multi_agent_workflow.md
├── requirements.txt
└── run.py



Notes and limitations

This is a deliberately scoped localhost implementation for an assignment, not a production crawler.

A few simplifications were intentionally made:

only HTML pages are indexed
there is no JavaScript rendering
robots.txt is not handled
relevance is simple keyword matching using term frequency
resume support is not fully implemented
the system is single-node only

Even with those limitations, the system satisfies the core requirements for crawling, search, visibility into system status, and multi-agent workflow documentation.

Included deliverables

The repository includes:

working crawler and search code
product_prd.md
readme.md
recommendation.md
multi_agent_workflow.md
agent description files under /agents

### Resume interrupted crawl jobs
ONEMLI 
The system includes basic resume support.

If an indexing job is interrupted, unfinished crawl jobs can be resumed using:

```bash
python -m app.main resume



Kaydet.

---

## 3) Final smoke test

```powershell
python -m app.main index https://example.com 1 --watch
python -m app.main search example
python -m app.main status
python -m app.main resume
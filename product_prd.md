# Product PRD — Multi-Agent Web Crawler and Search System

## 1. Overview

This project is a localhost-runnable web crawler and search system designed to run on a single machine. The system supports two core capabilities:

1. `index(origin, k)`  
   Starts a crawl from a given origin URL up to depth `k`, where depth represents the number of hops from the origin.

2. `search(query)`  
   Searches indexed content and returns relevant results in the form  
   `(relevant_url, origin_url, depth)`.

The project must be built using a multi-agent AI workflow during development. The final implementation does not need to be a runtime multi-agent system, but the design and implementation process must clearly show collaboration among multiple specialized AI agents.

## 2. Goals

- Build a working web crawler that runs on localhost
- Support controlled crawling with back pressure
- Ensure the same page is not crawled twice within the same crawl job
- Allow search to return relevant indexed pages
- Allow search to reflect newly indexed pages as the crawl progresses
- Provide a simple CLI for indexing, searching, and status inspection
- Document a clear multi-agent development workflow

## 3. Non-Goals

- Distributed crawling across multiple machines
- JavaScript rendering or browser automation
- Production-grade ranking quality
- Full-scale web search engine behavior
- Runtime autonomous agent collaboration inside the application itself

## 4. Functional Requirements

### 4.1 Index

The system must expose an indexing function:

`index(origin, k)`

Where:
- `origin` is the starting URL
- `k` is the maximum crawl depth

The crawler must:
- start from the origin URL
- crawl up to depth `k`
- normalize URLs before scheduling them
- avoid duplicate crawling within the same crawl job
- parse HTML pages and extract links
- store discovered pages and crawl metadata
- apply back pressure using bounded work queues and limited concurrency

### 4.2 Search

The system must expose a search function:

`search(query)`

Where:
- `query` is a string

The search system must:
- tokenize the query
- find relevant pages in the local index
- return results as triples:
  - `(relevant_url, origin_url, depth)`
- support searching while indexing is still active
- reflect newly indexed pages incrementally

### 4.3 CLI / UX

The project must provide a simple command-line interface that allows the user to:
- start an indexing job
- run a search query
- inspect system state

Example state information:
- active crawl jobs
- pages indexed
- queue depth
- pages in progress
- completed pages
- failed pages
- back pressure status

## 5. Non-Functional Requirements

- Must run entirely on localhost
- Must use a local database
- Must remain understandable and maintainable
- Must use mostly language-native functionality rather than full-featured crawler/search libraries
- Must be reasonably scalable on a single machine
- Must handle failures gracefully

## 6. Assumptions

- `index` is typically called before `search`
- Search may also be called while indexing is active
- Only HTML pages are indexed
- Relevance can be defined using a simple keyword-based approach
- SQLite is acceptable as the local database
- Python standard library tools are preferred

## 7. Architecture Overview

The system is divided into the following components:

### CLI Layer
Handles user commands:
- index
- search
- status

### Crawler Layer
Responsible for:
- frontier management
- worker threads
- fetch/parse/store pipeline
- duplicate prevention
- depth control

### Fetcher Layer
Responsible for:
- HTTP requests
- timeout handling
- content-type validation
- safe decoding of HTML

### Parser Layer
Responsible for:
- extracting links
- extracting visible text
- extracting page title
- generating tokens for indexing

### Storage Layer
Responsible for:
- storing crawl jobs
- storing frontier state
- storing pages
- storing discovery metadata
- storing inverted index data

### Search Layer
Responsible for:
- query tokenization
- index lookup
- relevance scoring
- returning results in required format

## 8. Storage Design

The local database should include tables such as:

### `crawl_jobs`
Stores crawl job metadata

### `frontier`
Stores URLs scheduled or processed for a given job

### `pages`
Stores page content and metadata

### `discoveries`
Stores the relationship between a discovered page, its origin, and its depth

### `inverted_index`
Stores search terms and page associations

The database should be configured to support concurrent reads during active writes where possible.

## 9. Concurrency and Back Pressure

The crawler should use:
- a bounded in-memory queue
- a fixed number of worker threads
- fetch timeouts
- controlled scheduling of discovered links

This ensures:
- controlled memory usage
- bounded work generation
- stable single-node execution

## 10. Search While Indexing

Search should be able to run while indexing is active.

Recommended approach:
- store page content incrementally as each page is processed
- update the inverted index immediately after parsing each page
- query the database directly from search

This allows newly indexed results to become searchable without waiting for the entire crawl to finish.

## 11. Multi-Agent Workflow Requirement

The project must be developed using multiple AI agents with clearly defined roles.

The workflow must include:
- agent definitions
- assigned responsibilities
- interaction between agents
- human review and final decision-making
- documentation of the workflow in `multi_agent_workflow.md`

Optional agent-specific files may be included in `/agents`.

## 12. Deliverables

The repository must include:

- working codebase
- `product_prd.md`
- `readme.md`
- `recommendation.md`
- `multi_agent_workflow.md`

Also included:
- agent description files under `/agents`

## 13. Implementation Priorities

1. Multi-agent workflow documentation
2. Agent description files
3. Project structure
4. Storage layer
5. URL normalization and parser
6. Fetcher
7. Crawler
8. Search
9. CLI
10. Final documentation polish

## 14. Success Criteria

The project is successful if:
- indexing works from a given origin up to depth `k`
- duplicate crawling is prevented within a job
- search returns relevant results in the correct format
- search can operate while indexing is active
- system state can be inspected from the CLI
- the development process clearly demonstrates multi-agent collaboration
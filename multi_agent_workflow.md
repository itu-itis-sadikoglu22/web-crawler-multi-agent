# Multi-Agent Workflow

## Overview

This project was developed using a multi-agent AI workflow rather than a single-agent coding process. The goal was not to build a runtime system of cooperating agents, but to use multiple specialized AI agents during the design and implementation process. Each agent was assigned a clear responsibility, produced recommendations or partial outputs, and contributed to the final solution.

The final implementation was selected and integrated by the human developer, who acted as the coordinator, reviewer, and final decision-maker.

## Why a Multi-Agent Workflow

The system being built has several distinct concerns:
- crawl orchestration
- URL normalization and duplicate prevention
- search indexing and relevance
- persistence and database schema
- architectural tradeoffs and system-level review

Instead of treating all of these as one undifferentiated coding task, the workflow separated them into focused agent responsibilities. This made it easier to reason about tradeoffs, compare alternatives, and document how decisions were made.

## Agents

### 1. Architect Agent
**Responsibility:**  
Design the overall system architecture.

**Focus areas:**  
- high-level components
- separation of concerns
- concurrency model
- back pressure strategy
- interaction between indexing and search

**Expected outputs:**  
- system architecture proposal
- module boundaries
- crawler/search integration plan
- identified risks and tradeoffs

---

### 2. Crawler Agent
**Responsibility:**  
Design the crawling workflow.

**Focus areas:**  
- crawl frontier management
- worker thread model
- URL normalization flow
- visited set behavior
- maximum depth handling
- duplicate crawl prevention

**Expected outputs:**  
- crawler loop design
- queue processing strategy
- link scheduling rules
- crawl job execution model

---

### 3. Search Agent
**Responsibility:**  
Design the indexing and retrieval approach.

**Focus areas:**  
- tokenization
- inverted index structure
- query matching
- simple relevance scoring
- how search can surface results while indexing is still active

**Expected outputs:**  
- indexing strategy
- search result format
- relevance assumptions
- incremental search update logic

---

### 4. Storage Agent
**Responsibility:**  
Design the persistence model.

**Focus areas:**  
- SQLite schema
- crawl jobs table
- frontier and discovery storage
- page storage
- inverted index storage
- concurrent read/write behavior
- resumability considerations

**Expected outputs:**  
- schema proposal
- storage layer responsibilities
- transaction model
- persistence tradeoffs

---

### 5. Reviewer Agent
**Responsibility:**  
Review the outputs of the other agents and identify conflicts, gaps, or weak assumptions.

**Focus areas:**  
- consistency between modules
- unhandled edge cases
- clarity of responsibilities
- architectural risks
- simplification opportunities

**Expected outputs:**  
- review notes
- conflict detection
- recommended adjustments
- final implementation concerns

---

## Human Role

The human developer was responsible for:
- defining the agents
- assigning responsibilities
- deciding the order in which agents contributed
- reviewing agent outputs
- resolving conflicts between recommendations
- selecting the final implementation
- writing and integrating the final code

In other words, the multi-agent workflow supported the design and implementation process, but the final engineering judgment remained human-led.

## Agent Interaction Model

The agents did not operate as an autonomous runtime system. Instead, they were used as structured contributors during development.

The interaction flow was:

1. **Architect Agent** proposed the high-level architecture.
2. **Storage Agent** proposed the persistence and schema design.
3. **Crawler Agent** proposed the crawl execution logic and queue model.
4. **Search Agent** proposed the indexing and retrieval logic.
5. **Reviewer Agent** evaluated the combined design and highlighted issues.
6. **Human developer** selected the final design decisions and implemented the code.

This workflow made the development process modular, explainable, and easier to evaluate.

## Example Decision Flow

One important design question was how search should work while indexing is still active.

- The **Architect Agent** proposed incremental indexing rather than batch-only indexing.
- The **Storage Agent** recommended SQLite in WAL mode to support concurrent reads during active writes.
- The **Search Agent** proposed updating the inverted index immediately after each page is parsed.
- The **Reviewer Agent** identified that this was sufficient for a single-node localhost system, while noting that a production deployment might require stronger separation between indexing and serving.

The human developer accepted this combined approach and used it in the final implementation.

## Example Conflict Resolution

Another design issue concerned duplicate prevention.

- One approach was to prevent duplicate crawling globally across all jobs.
- Another approach was to prevent duplicate crawling only within each crawl job.

The agents surfaced both options. The final implementation used per-job duplicate prevention as the minimum correctness guarantee, while still keeping the storage design compatible with future optimizations such as cross-job page reuse.

This was chosen because it met the project requirements while keeping the implementation simpler and easier to reason about.

## Development Principles Used in the Workflow

The multi-agent workflow followed these principles:
- each agent had a narrow, explicit role
- agent outputs were treated as proposals, not unquestioned truth
- architectural consistency mattered more than maximizing complexity
- the final implementation was kept intentionally simple and localhost-friendly
- the human developer remained the final integrator

## Files Associated with the Workflow

To make the workflow explicit, the project also includes agent description files under the `/agents` directory:

- `architect_agent.md`
- `crawler_agent.md`
- `search_agent.md`
- `storage_agent.md`
- `reviewer_agent.md`

These files describe each agent’s role, scope, and expected output more directly.

## Conclusion

This project demonstrates a multi-agent development process in which multiple AI agents contributed specialized design recommendations for a single-node web crawler and search system. The final codebase is not itself an autonomous multi-agent runtime, but the development workflow clearly reflects multi-agent collaboration, division of responsibilities, iterative review, and human-led integration.
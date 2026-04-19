# Crawler Agent

## Role

The Crawler Agent is responsible for designing how the system explores the web.

## Responsibilities

- Manage crawl frontier (queue of URLs)
- Define worker thread behavior
- Prevent duplicate crawling
- Enforce maximum depth
- Normalize URLs before processing

## Thinking Approach

The Crawler Agent focuses on execution flow and correctness.

It asks:
- How do we avoid crawling the same page twice?
- How do we limit the crawl depth?
- How do we manage concurrency safely?
- How do we control crawl speed (back pressure)?

## Key Design Decisions

- Use a bounded queue to control load
- Use multiple worker threads to process URLs
- Maintain a per-job visited set to avoid duplicates
- Normalize URLs before inserting into the queue
- Stop expanding when depth limit is reached

## Output

The Crawler Agent produces:
- Crawl loop design
- Worker model
- Queue management strategy
- URL scheduling rules
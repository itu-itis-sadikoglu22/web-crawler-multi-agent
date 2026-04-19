# Search Agent

## Role

The Search Agent is responsible for designing how indexed data is queried and returned.

## Responsibilities

- Define tokenization rules
- Design inverted index structure
- Implement relevance scoring
- Ensure search works during active indexing

## Thinking Approach

The Search Agent focuses on information retrieval.

It asks:
- How do we map words to pages?
- How do we rank results?
- How do we keep search fast?
- How can search reflect new data immediately?

## Key Design Decisions

- Use a simple inverted index stored in SQLite
- Tokenize text into lowercase words
- Store term frequencies per page
- Rank results by total term frequency
- Allow search to query DB while indexing is ongoing

## Output

The Search Agent produces:
- Indexing strategy
- Query logic
- Relevance assumptions
- Result format design
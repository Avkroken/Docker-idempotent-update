---
title: "Movie Filtering Logic"
wiki_page_id: "page-movie-logic"
---

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [filter_movies.py](../../../filter_movies.py)
- [README.md](../../../README.md)
- [AGENTS.md](../../../AGENTS.md)
- [CLAUDE.md](../../../CLAUDE.md)
- [SECURITY.md](../../../SECURITY.md)
- [filtered_movies_radarr.json](../../../filtered_movies_radarr.json)

</details>

# Movie Filtering Logic

The Movie Filtering Logic is a specialized system designed to programmatically identify high-value cinematic content for automated media management. Its primary purpose is to filter the vast database of The Movie Database (TMDb) to find big-budget productions released within the current calendar year. This filtered data is specifically formatted for direct consumption by Radarr via the StevenLu custom list format.

Sources: [README.md:1-12](README.md#L1-L12), [filter_movies.py:1-15](filter_movies.py#L1-L15), [AGENTS.md:1-10](AGENTS.md#L1-L10)

## Core Filtering Criteria

The system applies a strict set of rules to determine which movies are included in the final output. The philosophy behind this logic is that high financial investment signifies industry importance, regardless of critical reception or ratings.

| Criterion | Requirement | Logic Description |
|-----------|-------------|-------------------|
| **Budget** | ≥ $100,000,000 | Only movies with a production budget of 100 million USD or more are retained. |
| **Release Date** | Current Year | Movies must have been released between January 1st of the current year and today. |
| **Identity** | IMDb ID Required | Movies lacking an IMDb ID are skipped as they cannot be effectively tracked in Radarr. |
| **Data Integrity** | Budget > 0 | TMDb returns 0 for unknown budgets; these are discarded to prevent false positives. |

Sources: [filter_movies.py:35](filter_movies.py#L35), [filter_movies.py:97-120](filter_movies.py#L97-L120), [README.md:15-20](README.md#L15-L20)

## Architecture and Data Flow

The logic follows a three-stage process: Discovery, Detailed Evaluation, and Formatting. This structure optimizes API usage by first identifying potential candidates before performing resource-intensive detailed lookups.

### Discovery and Filtering Flow

The following diagram illustrates the sequential logic from initial TMDb API calls to the final JSON output.

```mermaid
flowchart TD
    Start([Start Script]) --> Auth[Check TMDB_API_KEY]
    Auth --> Discovery[Discovery Phase: Fetch IDs]
    
    subgraph Discovery_Phase [Discovery Phase]
    Discovery --> NP[/movie/now_playing]
    Discovery --> Pop[/discover/movie?sort=popularity]
    Discovery --> Rev[/discover/movie?sort=revenue]
    end
    
    Discovery_Phase --> Dedupe[Deduplicate Movie IDs]
    Dedupe --> Loop{For each ID}
    
    subgraph Evaluation [Evaluation Phase]
    Loop --> Fetch[Fetch Full Movie Details]
    Fetch --> DateCheck{Released this year?}
    DateCheck -- No --> Skip[Skip Movie]
    DateCheck -- Yes --> BudgetCheck{Budget >= $100M?}
    BudgetCheck -- No --> Skip
    BudgetCheck -- Yes --> IMDBCheck{Has IMDb ID?}
    IMDBCheck -- No --> Skip
    IMDBCheck -- Yes --> Format[Map to StevenLu Format]
    end
    
    Format --> Collect[Add to Filtered List]
    Skip --> Loop
    Collect --> Sort[Sort by Title]
    Sort --> Write[Write to filtered_movies_radarr.json]
    Write --> End([End Script])
```

The system utilizes multiple TMDb endpoints, including `/movie/now_playing` and various `/discover/movie` queries sorted by popularity, vote count, and revenue to ensure comprehensive coverage. 
Sources: [filter_movies.py:46-77](filter_movies.py#L46-L77), [filter_movies.py:91-137](filter_movies.py#L91-L137)

## Technical Implementation Details

### Configuration and Environment
The script requires a `TMDB_API_KEY` provided as a Read Access Token (JWT) through environment variables. It also integrates with Sentry for error tracking.

```python
# Configuration constants
OUTPUT_FILE = "filtered_movies_radarr.json"
MIN_BUDGET = 100_000_000  # $100M

HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}
```

Sources: [filter_movies.py:31-42](filter_movies.py#L31-L42), [SECURITY.md:58-65](SECURITY.md#L58-L65)

### Rate Limiting and Error Handling
The implementation includes defensive programming measures to handle API limitations and network issues:
*  **Status 429 Handling**: If the TMDb API returns a "Too Many Requests" status, the script sleeps for 2 seconds before retrying.
*  **Timeouts**: All requests are capped at a 30-second timeout.
*  **Exception Safety**: Individual movie fetch failures within a loop do not terminate the entire process; they are logged, and the loop continues.

Sources: [filter_movies.py:65-68](filter_movies.py#L65-L68), [filter_movies.py:101-105](filter_movies.py#L101-L105)

### Data Transformation (StevenLu Format)
To ensure compatibility with Radarr, the complex movie objects returned by TMDb are simplified into a specific schema.

```json
[
  {
    "title": "Project Hail Mary",
    "imdb_id": "tt12042730"
  }
]
```

The function `simplify_movie_stevenlu` handles this mapping, extracting only the `title` and `imdb_id` fields.
Sources: [filter_movies.py:80-88](filter_movies.py#L80-L88), [README.md:61-72](README.md#L61-L72), [filtered_movies_radarr.json:1-35](filtered_movies_radarr.json#L1-L35)

## Security and Operational Constraints

The Movie Filtering Logic is governed by strict operational security policies to prevent credential leakage and ensure reliable automated execution.

*  **Credential Masking**: Secrets are never hardcoded and are injected via GitHub Secrets (`TMDB_API_KEY`) during the daily GitHub Actions workflow.
*  **Automation**: The logic runs daily at 06:00 UTC via `update-movies.yml`.
*  **Commit Logic**: Automated updates to the JSON output files must NOT include `[skip ci]` in the commit message to ensure that mandatory repository checks are performed on resulting Pull Requests.

Sources: [SECURITY.md:1-10](SECURITY.md#L1-L10), [CLAUDE.md:15-32](CLAUDE.md#L15-L32), [README.md:100-110](README.md#L100-L110)

## Summary
The Movie Filtering Logic provides a targeted, automated pipeline for identifying "tentpole" cinema productions. By combining financial thresholds with chronological filters and strictly defined output schemas, it enables automated media managers like Radarr to track high-budget releases with minimal manual intervention.

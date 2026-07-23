---
title: "Python Script: filter_tv_shows.py"
wiki_page_id: "page-script-tv"
---

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [filter_tv_shows.py](../../../filter_tv_shows.py)
- [filter_movies.py](../../../filter_movies.py)
- [README.md](../../../README.md)
- [AGENTS.md](../../../AGENTS.md)
- [CLAUDE.md](../../../CLAUDE.md)
- [filtered_tv_shows_sonarr.json](../../../filtered_tv_shows_sonarr.json)
</details>

# Python Script: filter_tv_shows.py

The `filter_tv_shows.py` script is a core automation component of the `filtered-movies` project designed to identify and curate high-value television content. Its primary purpose is to query The Movie Database (TMDb) API to find new TV shows that premiered within the current calendar year on specific "prestige" networks and streaming platforms.

The script produces a specialized JSON output file, `filtered_tv_shows_sonarr.json`, which is formatted for direct consumption by Sonarr's Custom List import feature. This automation ensures that users have an up-to-date list of major series premieres without manual tracking.

Sources: [filter_tv_shows.py:1-18](filter_tv_shows.py#L1-L18), [README.md:1-20](README.md#L1-L20), [AGENTS.md:1-12](AGENTS.md#L1-L12)

## Core Logic and Filtering Criteria

The script follows a strict multi-stage filtering process to ensure only high-quality, relevant shows are included in the final export.

### Filtering Rules
To qualify for the list, a TV show must meet three primary criteria:
1.  **Release Date:** The show must have premiered on or after January 1st of the current year.
2.  **Prestige Network:** The show must be associated with one of the predefined "top-tier" networks or streaming services.
3.  **Metadata Requirement:** The show must possess a valid TVDB ID, as this is the mandatory identifier used by Sonarr for custom list imports.

Sources: [filter_tv_shows.py:11-16](filter_tv_shows.py#L11-L16), [README.md:28-39](README.md#L28-L39)

### Targeted Networks
The script maintains a list of "Prestige Networks" used to filter the TMDb results. If a show's network list contains any of these strings (case-insensitive), it is considered a prestige show.

| Network Category | Included Keywords |
| :--- | :--- |
| **Amazon** | Amazon, Prime Video, Amazon Prime Video |
| **Apple** | Apple TV+, Apple TV |
| **HBO** | HBO, Max |
| **Other** | National Geographic |

Sources: [filter_tv_shows.py:44-53](filter_tv_shows.py#L44-L53), [README.md:32-37](README.md#L32-L37)

## Architecture and Data Flow

The script operates in a linear execution flow: initializing environment variables, gathering potential show IDs from multiple TMDb endpoints, fetching detailed metadata for each show, applying filters, and finally writing the results to disk.

### System Flow Diagram
The following diagram illustrates the internal logic from execution start to JSON generation.

```mermaid
flowchart TD
    Start([Start Script]) --> EnvCheck{Check API Key}
    EnvCheck -- Missing --> Exit[Exit Error]
    EnvCheck -- Present --> GetIDs[Get TV IDs from TMDb]
    
    subgraph Discovery [Discovery Phase]
    GetIDs --> OnAir[/tv/on_the_air]
    GetIDs --> AiringToday[/tv/airing_today]
    GetIDs --> Discover[/discover/tv]
    end
    
    Discovery --> DetailFetch[Fetch Show Details + External IDs]
    
    subgraph Filtering [Filtering Phase]
    DetailFetch --> YearCheck{Premiered this year?}
    YearCheck -- Yes --> NetCheck{Prestige Network?}
    NetCheck -- Yes --> IDCheck{Has TVDB ID?}
    end
    
    IDCheck -- Yes --> Collect[Add to Filtered List]
    Collect --> Save[Write to filtered_tv_shows_sonarr.json]
    Save --> End([End Script])
```

The script uses multiple TMDb endpoints to ensure maximum coverage of new releases.
Sources: [filter_tv_shows.py:64-106](filter_tv_shows.py#L64-L106), [filter_tv_shows.py:126-160](filter_tv_shows.py#L126-L160)

## Implementation Details

### API Interaction
The script interacts with the TMDb API (v3) using a Read Access Token (Bearer Token). It implements basic error handling for common API issues.

*  **Authentication:** Utilizes the `TMDB_API_KEY` environment variable.
*  **Rate Limiting:** Handles HTTP 429 (Too Many Requests) by pausing execution (`time.sleep`) before retrying.
*  **Timeout:** Requests are configured with a 30-second timeout to prevent hanging.

Sources: [filter_tv_shows.py:40-42](filter_tv_shows.py#L40-L42), [filter_tv_shows.py:99-102](filter_tv_shows.py#L99-L102), [CLAUDE.md:25-27](CLAUDE.md#L25-L27)

### Key Functions

| Function | Purpose |
| :--- | :--- |
| `get_tv_show_ids` | Iterates through multiple discovery endpoints to build a unique set of TV show IDs from the current year. |
| `is_prestige_show` | Inspects the `networks` attribute of a show object to match against the `PRESTIGE_NETWORKS` list. |
| `fetch_and_filter_shows` | Performs the `append_to_response=external_ids` query for each ID to retrieve TVDB identifiers and final metadata. |
| `main` | Orchestrates the process, handles logging to the console, and writes the final JSON output. |

Sources: [filter_tv_shows.py:64](filter_tv_shows.py#L64), [filter_tv_shows.py:112](filter_tv_shows.py#L112), [filter_tv_shows.py:121](filter_tv_shows.py#L121), [filter_tv_shows.py:175](filter_tv_shows.py#L175)

### Monitoring and Observability
The script integrates with Sentry via `sentry-sdk`. This is used to capture exceptions during the daily automated runs in GitHub Actions. Because the script is short-lived, it explicitly calls `sentry_sdk.flush()` to ensure all queued events are sent before the process terminates.

Sources: [filter_tv_shows.py:27-33](filter_tv_shows.py#L27-L33), [filter_tv_shows.py:206-213](filter_tv_shows.py#L206-L213)

## Output Format

The output file `filtered_tv_shows_sonarr.json` is a simplified JSON array of objects. Each object contains exactly one key, `TvdbId`, as required by the Sonarr Custom List specification.

```json
[
  {
    "TvdbId": 376098
  },
  {
    "TvdbId": 430654
  }
]
```

Sources: [filtered_tv_shows_sonarr.json:1-8](filtered_tv_shows_sonarr.json#L1-L8), [README.md:83-88](README.md#L83-L88)

## Conclusion
The `filter_tv_shows.py` script provides a automated bridge between TMDb's vast database and Sonarr's management capabilities. By focusing exclusively on high-profile network premieres within the current year, it maintains a focused "prestige" list that simplifies the discovery and tracking of major television series.

---
title: "Customizing Filter Criteria"
wiki_page_id: "page-custom-filters"
---

<details>
<summary>Relevant source files</summary>

The following files were used as context for generating this wiki page:

- [filter\_movies.py](filter_movies.py)
- [filter\_tv\_shows.py](filter_tv_shows.py)
- [README.md](README.md)
- [AGENTS.md](AGENTS.md)
- [CLAUDE.md](CLAUDE.md)
</details>

# Customizing Filter Criteria

The filtering system in this project is designed to curate high-value media content from The Movie Database (TMDb) for automated import into Radarr and Sonarr. The criteria are hardcoded into specific Python scripts to ensure a "big budget" and "prestige network" selection philosophy, prioritizing production value over user ratings.

Sources: [README.md:14-25](README.md#L14-L25), [AGENTS.md:10-14](AGENTS.md#L10-L14)

## Movie Filtering (Radarr)

Movie filtering is governed by `filter_movies.py`. The primary objective is to identify "Blockbuster" content based on financial investment and release timing.

### Budget and Temporal Constraints
The script defines a strict financial threshold and a rolling date window:
*  **Minimum Budget:** Set at $100,000,000. Movies with unreported budgets (returning 0 from the API) are automatically excluded to prevent false positives.
*  **Release Window:** Limited to the current calendar year up to the current date.

Sources: [filter_movies.py:31-33](filter_movies.py#L31-L33), [filter_movies.py:85-88](filter_movies.py#L85-L88), [filter_movies.py:98-100](filter_movies.py#L98-L100)

### Data Acquisition Flow
The system aggregates movie IDs from multiple TMDb endpoints to ensure comprehensive coverage before applying individual filters.

```mermaid
graph TD
    A[Start filter_movies.py] --> B[Fetch Movie IDs]
    B --> B1[/movie/now_playing]
    B --> B2[/discover/movie - Popularity]
    B --> B3[/discover/movie - Vote Count]
    B --> B4[/discover/movie - Revenue]
    B1 & B2 & B3 & B4 --> C[Fetch Individual Movie Details]
    C --> D{Budget >= $100M?}
    D -- No --> E[Discard]
    D -- Yes --> F{Has IMDb ID?}
    F -- No --> G[Log Skip]
    F -- Yes --> H[Add to filtered_movies_radarr.json]
```

The diagram shows the multi-endpoint discovery process and the sequential budget and metadata validation steps. 
Sources: [filter_movies.py:46-64](filter_movies.py#L46-L64), [filter_movies.py:102-118](filter_movies.py#L102-L118)

## TV Show Filtering (Sonarr)

TV show filtering is governed by `filter_tv_shows.py`. Unlike movies, TV shows are filtered by the reputation of the producing network or streaming service.

### Prestige Network Selection
The filter identifies shows from a specific list of "Prestige Networks." The matching logic is case-insensitive and supports partial string matches (e.g., "Amazon" matches "Amazon Prime Video").

| Target Network | Included Variations/Aliases |
| :--- | :--- |
| HBO | HBO, Max |
| Apple | Apple TV+, Apple TV |
| Amazon | Amazon, Prime Video, Amazon Prime Video |
| National Geographic | National Geographic |

Sources: [filter_tv_shows.py:40-49](filter_tv_shows.py#L40-L49), [filter_tv_shows.py:100-106](filter_tv_shows.py#L100-L106)

### TV Show Filtering Logic
The script requires a TVDB ID for every entry, as this is the mandatory identifier for Sonarr Custom Lists.

```mermaid
flowchart TD
    Start[Fetch TV IDs] --> Endpoints{Endpoints}
    Endpoints --> E1[/tv/on_the_air]
    Endpoints --> E2[/tv/airing_today]
    Endpoints --> E3[/discover/tv]
    E1 & E2 & E3 --> Details[Fetch Show Details]
    Details --> DateCheck{Premiered This Year?}
    DateCheck -- No --> Skip[Discard]
    DateCheck -- Yes --> NetCheck{On Prestige Network?}
    NetCheck -- No --> Skip
    NetCheck -- Yes --> IDCheck{Has TVDB ID?}
    IDCheck -- No --> Skip
    IDCheck -- Yes --> Save[Add to filtered_tv_shows_sonarr.json]
```

This flowchart illustrates the hierarchical filtering process: first by date, then by network affiliation, and finally by metadata availability.
Sources: [filter_tv_shows.py:58-75](filter_tv_shows.py#L58-L75), [filter_tv_shows.py:126-146](filter_tv_shows.py#L126-L146)

## Configuration and Implementation Details

### Environment Variables
Both scripts require authentication via the TMDb API.

| Variable | Description | Requirement |
| :--- | :--- | :--- |
| `TMDB_API_KEY` | TMDb API Read Access Token (starts with `eyJ...`) | Mandatory |
| `SENTRY_DSN` | Sentry Data Source Name for error tracking | Optional |

Sources: [filter_movies.py:25-29](filter_movies.py#L25-L29), [filter_tv_shows.py:34-38](filter_tv_shows.py#L34-L38), [CLAUDE.md:21-25](CLAUDE.md#L21-L25)

### Output Specifications
The filters generate JSON files compatible with specific import list formats.

```python
# filter_movies.py: StevenLu Format
{
    "title": movie.get("title"),
    "imdb_id": imdb_id
}

# filter_tv_shows.py: Sonarr Custom List Format
{
    "TvdbId": tvdb_id
}
```

Sources: [filter_movies.py:76-82](filter_movies.py#L76-L82), [filter_tv_shows.py:148](filter_tv_shows.py#L148)

## Conclusion
The customization logic is centralized in the `PRESTIGE_NETWORKS` list for TV shows and the `MIN_BUDGET` constant for movies. By modifying these hardcoded values in `filter_tv_shows.py` and `filter_movies.py`, developers can easily shift the filtering criteria to target different content tiers or specific networks as the media landscape evolves.

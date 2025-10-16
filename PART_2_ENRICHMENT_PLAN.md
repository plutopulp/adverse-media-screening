# Part 2: Automated Entity Enrichment Plan

## Problem

Articles rarely include full names or dates of birth, which means we often end up with "possible" or "probable" matches that analysts have to investigate manually.

## Proposed Solution

When we get an uncertain match, automatically search the web for the missing details using what we learnt from the article (their job, company, location, relationship to other entities in the articles etc.), then re-run the matching with the new data.

## Architecture

```
Screening Pipeline
    ↓
Match < definite_match?
    ↓ Yes
Enrichment Orchestrator
    ├─ Select strategies based on context
    ├─ Execute parallel searches
    │   ├─ Professional networks
    │   ├─ Company websites
    │   ├─ News archives
    │   └─ LLM web search (fallback)
    ↓
Validate & Aggregate Results
    ↓
Update Entity → Re-run Matching → Improved Confidence
```

## Core Components

**Enrichment Orchestrator**

- Decides which entities need enriching (only the uncertain matches)
- Picks search strategies based on what context we have (roles, organisations, locations)
- Aggregates and validates results

**Search Strategies (Plugin Architecture)**

Each strategy says when it's applicable, has a priority level, and returns structured data with confidence scores:

- **Professional Networks** - Search profile sites using employment history
- **Company Websites** - Check employer sites for bios (leadership pages, press releases)
- **News Archives** - Search historical articles for biographical details (ages → DOB)
- **LLM Web Search** - Fallback using LLM with web access to synthesise information
- **Public Records** - Optional, jurisdiction-dependent, needs legal review

**Result Validation**

- Deduplicate findings across sources
- Consistency checks (e.g. if multiple sources say different DOBs, flag it)
- Cross-reference with article context
- Confidence scoring (multiple agreeing sources boost confidence)
- Flag conflicts

**Pipeline Integration**

- Trigger after initial matching when confidence < definite match
- Update entity with enriched data (middle names, DOB etc..)
- Re-run matcher with updated entities
- Track enrichment attempts in result for audit trail

## Data Flow

1. Use previously extracted context from entity (name, roles, organisations, locations, relationships)
2. Run strategies in priority order (stop early if we find high-confidence data)
3. Validate findings (consistency checks, confidence scoring)
4. Apply enriched data to entity
5. Re-run matching → should see confidence improve

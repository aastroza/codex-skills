---
name: scryfall-api
description: "Call the Scryfall REST API for Magic: The Gathering card data. Use when Codex needs to look up cards by exact or fuzzy name, run Scryfall search syntax queries, retrieve rulings, sets, catalogs, random cards, collection matches, card images, prices, legality, or bulk data download metadata from Scryfall."
---

# Scryfall API

## Quick Start

Use `scripts/scryfall_api.py` for common requests. It handles JSON encoding, user-agent headers, pagination, POST bodies, and Scryfall error responses.

```bash
python scripts/scryfall_api.py named "Lightning Bolt" --format summary
python scripts/scryfall_api.py search "type:legendary type:creature color=uw" --max-pages 1 --format summary --limit 10
python scripts/scryfall_api.py rulings 77c6fa74-5543-42ac-9ead-0e890b188e99
python scripts/scryfall_api.py bulk-data default_cards
python scripts/scryfall_api.py get /cards/search --param "q=o:draw t:instant" --param "unique=cards"
```

Read `references/api.md` when constructing less common endpoints or when the script needs to be patched for a new operation.

## Workflow

1. Prefer live API calls for current card data, legality, pricing, set metadata, rulings, and bulk file URLs.
2. Use Scryfall search syntax in `search` queries instead of filtering locally when the API can express the request.
3. Use `named` for single-card lookup. Default to fuzzy matching when the user may have misspelled a name; use `--exact` when precision matters.
4. Use `collection` for decklists or batches of known names, IDs, or set collector numbers.
5. Use `bulk-data` for large offline analysis instead of crawling paginated search results.
6. Return concise summaries to users unless they explicitly ask for raw JSON, image URLs, prices, or all fields.

## Land And Mana Base Searches

- Do not rely only on Oracle text searches such as `o:"{R} or {G}"` when looking for lands or mana fixing. Lands with basic land types, such as shocklands, surveil lands, and triomes, get mana abilities from their subtypes, so those abilities may not appear in `oracle_text`.
- For mana bases, search both Oracle text and type/subtype. Use exact-name lookups for known land cycles before concluding a fixing option is unavailable.
- When a deck's colors are known, explicitly verify the obvious premium cycles for those colors: shocklands, fastlands, painlands, checklands, pathways, surveil lands, triomes, verges, manlands, and format-specific duals.
- For typed duals, use type/subtype queries such as `legal:standard t:land type:mountain type:forest`, `legal:standard t:land type:island type:mountain`, or `legal:standard t:land type:forest type:island` instead of only `o:` text.
- For final decklists, run exact-name legality checks on every land that materially affects the mana base. Do not infer legality from adjacent cycles or from memory.
- If a Scryfall search misses an expected staple, test by exact name before rejecting it. A missing result from a broad query is not proof that the card is illegal or unavailable.

## API Practices

- Set a clear `User-Agent` and `Accept: application/json`.
- Respect pagination: Scryfall list objects may include `has_more` and `next_page`.
- Add a small delay between paginated requests and back off if a 429 response occurs.
- Do not scrape card pages when the API has the field. Card objects include `image_uris`, `card_faces`, `prices`, `legalities`, `purchase_uris`, and related API URIs.
- Treat prices and legality as current only at request time.
- For multi-faced cards, inspect `card_faces`; some fields may live on faces rather than the top-level card object.

## Useful Commands

Lookup by name:

```bash
python scripts/scryfall_api.py named "Sol Ring" --exact --format summary
```

Search with Scryfall syntax:

```bash
python scripts/scryfall_api.py search "commander:legal id<=esper t:legendary" --all --format summary
```

Search lands by subtype, not only Oracle text:

```bash
python scripts/scryfall_api.py search "legal:standard t:land type:mountain type:forest" --format summary
python scripts/scryfall_api.py search "legal:standard t:land (type:forest type:island or o:\"{G} or {U}\" or o:\"{U} or {G}\")" --format summary
python scripts/scryfall_api.py named "Stomping Ground" --exact --format summary
```

Batch identify a list:

```bash
python scripts/scryfall_api.py collection --name "Island" --name "Counterspell" --set-number "lea:233"
```

Retrieve arbitrary GET endpoints:

```bash
python scripts/scryfall_api.py get /sets
python scripts/scryfall_api.py get /catalog/card-names
```

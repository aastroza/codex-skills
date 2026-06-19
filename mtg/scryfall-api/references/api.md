# Scryfall API Reference

Base URL: `https://api.scryfall.com`

The API is unauthenticated and returns JSON. Send `Accept: application/json` and a descriptive `User-Agent`.

## Common Endpoints

- `GET /cards/named?fuzzy=<name>`: best-effort card lookup by name.
- `GET /cards/named?exact=<name>`: exact card lookup by name.
- `GET /cards/search?q=<syntax>`: search using Scryfall search syntax. Common params: `unique`, `order`, `dir`, `include_extras`, `include_multilingual`, `include_variations`, `page`.
- `GET /cards/autocomplete?q=<prefix>`: autocomplete card names.
- `GET /cards/random` or `/cards/random?q=<syntax>`: random matching card.
- `GET /cards/<id>`: card by Scryfall UUID.
- `GET /cards/<id>/rulings`: rulings for a card.
- `POST /cards/collection`: identify up to 75 cards per request using identifiers.
- `GET /sets` and `GET /sets/<code-or-id>`: set data.
- `GET /bulk-data` and `GET /bulk-data/<type-or-id>`: bulk file metadata and download URLs.
- `GET /catalog/<name>`: catalogs such as `card-names`, `artist-names`, `word-bank`, `creature-types`, `planeswalker-types`, `land-types`, `artifact-types`, `enchantment-types`, `spell-types`, `powers`, `toughnesses`, `loyalties`, `keyword-abilities`, `keyword-actions`, `ability-words`.

## Search Notes

Prefer server-side Scryfall syntax:

- `name:bolt`, `!"Lightning Bolt"`, `o:"draw a card"`, `type:legendary`, `t:creature`
- `id<=esper`, `c=uw`, `mv<=3`, `pow>=4`, `tou<3`
- `set:mh3`, `rarity:mythic`, `artist:"Rebecca Guay"`
- `legal:commander`, `banned:modern`, `game:arena`, `is:funny`, `is:extra`

Use URL encoding through a client library rather than hand-building query strings.

## Card Object Fields To Check

- Identity: `id`, `oracle_id`, `name`, `lang`, `released_at`
- Text: `mana_cost`, `type_line`, `oracle_text`, `power`, `toughness`, `loyalty`, `keywords`
- Faces: `card_faces` for transform, modal double-faced, split, aftermath, and other multi-part layouts
- Images: top-level `image_uris` or per-face `card_faces[].image_uris`
- Gameplay: `legalities`, `games`, `reserved`, `edhrec_rank`
- Printing: `set`, `set_name`, `collector_number`, `rarity`, `finishes`, `promo`, `reprint`
- Economy: `prices`, `purchase_uris`
- Links: `scryfall_uri`, `rulings_uri`, `prints_search_uri`

## Error Handling

Scryfall error responses are JSON objects with fields such as `object`, `code`, `status`, `details`, and sometimes `warnings`. Surface `details` to the user and do not retry invalid queries. Retry or back off only for transient network errors and 429 responses.

#!/usr/bin/env python3
"""Small CLI wrapper for the Scryfall REST API."""

from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


BASE_URL = "https://api.scryfall.com"
USER_AGENT = "CodexScryfallSkill/1.0"


class ScryfallError(RuntimeError):
    pass


if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
if hasattr(sys.stderr, "reconfigure"):
    sys.stderr.reconfigure(encoding="utf-8")


def request_json(
    method: str,
    path_or_url: str,
    params: dict[str, Any] | None = None,
    body: dict[str, Any] | None = None,
) -> Any:
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        url = path_or_url
    else:
        path = path_or_url if path_or_url.startswith("/") else f"/{path_or_url}"
        url = f"{BASE_URL}{path}"

    if params:
        clean_params = {k: v for k, v in params.items() if v is not None}
        query = urllib.parse.urlencode(clean_params, doseq=True)
        separator = "&" if "?" in url else "?"
        url = f"{url}{separator}{query}"

    data = None
    if body is not None:
        data = json.dumps(body).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        method=method.upper(),
        headers={
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            payload = json.loads(raw)
            detail = payload.get("details") or payload.get("code") or raw
        except json.JSONDecodeError:
            detail = raw
        raise ScryfallError(f"HTTP {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ScryfallError(f"Network error: {exc.reason}") from exc


def get_all_pages(first: Any, max_pages: int | None = None) -> Any:
    if not isinstance(first, dict) or first.get("object") != "list":
        return first

    combined = dict(first)
    data = list(first.get("data", []))
    next_page = first.get("next_page")
    pages = 1

    while next_page and (max_pages is None or pages < max_pages):
        time.sleep(0.12)
        page = request_json("GET", next_page)
        data.extend(page.get("data", []))
        next_page = page.get("next_page")
        pages += 1

    combined["data"] = data
    combined["has_more"] = bool(next_page)
    if next_page:
        combined["next_page"] = next_page
    else:
        combined.pop("next_page", None)
    return combined


def card_faces_text(card: dict[str, Any]) -> str:
    if "card_faces" not in card:
        return card.get("oracle_text", "")
    parts = []
    for face in card.get("card_faces", []):
        text = face.get("oracle_text", "")
        parts.append(f"{face.get('name', '')}: {text}".strip())
    return "\n// ".join(parts)


def summarize_card(card: dict[str, Any]) -> dict[str, Any]:
    image_uris = card.get("image_uris")
    if not image_uris and card.get("card_faces"):
        image_uris = card["card_faces"][0].get("image_uris")

    return {
        "name": card.get("name"),
        "mana_cost": card.get("mana_cost"),
        "type_line": card.get("type_line"),
        "oracle_text": card_faces_text(card),
        "set": card.get("set"),
        "set_name": card.get("set_name"),
        "collector_number": card.get("collector_number"),
        "rarity": card.get("rarity"),
        "legalities": card.get("legalities"),
        "prices": card.get("prices"),
        "image_normal": image_uris.get("normal") if image_uris else None,
        "scryfall_uri": card.get("scryfall_uri"),
    }


def summarize(payload: Any, limit: int | None = None) -> Any:
    if isinstance(payload, dict) and payload.get("object") == "card":
        return summarize_card(payload)
    if isinstance(payload, dict) and payload.get("object") == "list":
        items = payload.get("data", [])
        if limit is not None:
            items = items[:limit]
        return {
            "object": "list",
            "total_cards": payload.get("total_cards"),
            "has_more": payload.get("has_more"),
            "count": len(payload.get("data", [])),
            "shown": len(items),
            "data": [
                summarize_card(item) if isinstance(item, dict) and item.get("object") == "card" else item
                for item in items
            ],
        }
    return payload


def print_payload(payload: Any, fmt: str, limit: int | None = None) -> None:
    if fmt == "summary":
        payload = summarize(payload, limit=limit)
    print(json.dumps(payload, indent=2, ensure_ascii=False, sort_keys=False))


def parse_param(values: list[str]) -> dict[str, str]:
    params: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"--param must be key=value, got: {value}")
        key, raw = value.split("=", 1)
        params[key] = raw
    return params


def add_common_format(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--format", choices=["json", "summary"], default="json")
    parser.add_argument("--limit", type=int, help="Limit list items shown in summary output.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Call the Scryfall REST API.")
    sub = parser.add_subparsers(dest="command", required=True)

    named = sub.add_parser("named", help="Find a card by exact or fuzzy name.")
    named.add_argument("name")
    named.add_argument("--exact", action="store_true")
    named.add_argument("--set", dest="set_code")
    add_common_format(named)

    search = sub.add_parser("search", help="Search cards with Scryfall syntax.")
    search.add_argument("query")
    search.add_argument("--unique", default="cards")
    search.add_argument("--order", default="name")
    search.add_argument("--dir", default="auto")
    search.add_argument("--include-extras", action="store_true")
    search.add_argument("--include-multilingual", action="store_true")
    search.add_argument("--include-variations", action="store_true")
    search.add_argument("--page", type=int)
    search.add_argument("--all", action="store_true", help="Follow all result pages.")
    search.add_argument("--max-pages", type=int, default=1)
    add_common_format(search)

    autocomplete = sub.add_parser("autocomplete", help="Autocomplete card names.")
    autocomplete.add_argument("query")
    add_common_format(autocomplete)

    random_card = sub.add_parser("random", help="Fetch a random card.")
    random_card.add_argument("--query")
    add_common_format(random_card)

    sets = sub.add_parser("sets", help="List all sets.")
    add_common_format(sets)

    set_cmd = sub.add_parser("set", help="Fetch one set by code or ID.")
    set_cmd.add_argument("code_or_id")
    add_common_format(set_cmd)

    rulings = sub.add_parser("rulings", help="Fetch rulings for a card UUID.")
    rulings.add_argument("card_id")
    add_common_format(rulings)

    bulk = sub.add_parser("bulk-data", help="Fetch bulk data metadata.")
    bulk.add_argument("type_or_id", nargs="?")
    add_common_format(bulk)

    catalog = sub.add_parser("catalog", help="Fetch a Scryfall catalog.")
    catalog.add_argument("name")
    add_common_format(catalog)

    collection = sub.add_parser("collection", help="Identify cards in a batch.")
    collection.add_argument("--name", action="append", default=[])
    collection.add_argument("--id", action="append", default=[])
    collection.add_argument("--oracle-id", action="append", default=[])
    collection.add_argument("--multiverse-id", action="append", type=int, default=[])
    collection.add_argument("--set-number", action="append", default=[], help="Use set:collector_number.")
    add_common_format(collection)

    get = sub.add_parser("get", help="GET any Scryfall API path.")
    get.add_argument("path")
    get.add_argument("--param", action="append", default=[])
    add_common_format(get)

    return parser


def collection_identifiers(args: argparse.Namespace) -> list[dict[str, Any]]:
    identifiers: list[dict[str, Any]] = []
    identifiers.extend({"name": name} for name in args.name)
    identifiers.extend({"id": card_id} for card_id in args.id)
    identifiers.extend({"oracle_id": oracle_id} for oracle_id in args.oracle_id)
    identifiers.extend({"multiverse_id": multiverse_id} for multiverse_id in args.multiverse_id)
    for value in args.set_number:
        if ":" not in value:
            raise SystemExit("--set-number must be formatted as set:collector_number")
        set_code, collector_number = value.split(":", 1)
        identifiers.append({"set": set_code, "collector_number": collector_number})
    if not identifiers:
        raise SystemExit("collection requires at least one identifier")
    return identifiers


def run(args: argparse.Namespace) -> Any:
    if args.command == "named":
        key = "exact" if args.exact else "fuzzy"
        params = {key: args.name, "set": args.set_code}
        return request_json("GET", "/cards/named", params=params)

    if args.command == "search":
        params = {
            "q": args.query,
            "unique": args.unique,
            "order": args.order,
            "dir": args.dir,
            "include_extras": str(args.include_extras).lower(),
            "include_multilingual": str(args.include_multilingual).lower(),
            "include_variations": str(args.include_variations).lower(),
            "page": args.page,
        }
        first = request_json("GET", "/cards/search", params=params)
        max_pages = None if args.all else args.max_pages
        return get_all_pages(first, max_pages=max_pages)

    if args.command == "autocomplete":
        return request_json("GET", "/cards/autocomplete", params={"q": args.query})

    if args.command == "random":
        return request_json("GET", "/cards/random", params={"q": args.query})

    if args.command == "sets":
        return request_json("GET", "/sets")

    if args.command == "set":
        return request_json("GET", f"/sets/{args.code_or_id}")

    if args.command == "rulings":
        return request_json("GET", f"/cards/{args.card_id}/rulings")

    if args.command == "bulk-data":
        path = "/bulk-data" if not args.type_or_id else f"/bulk-data/{args.type_or_id}"
        return request_json("GET", path)

    if args.command == "catalog":
        return request_json("GET", f"/catalog/{args.name}")

    if args.command == "collection":
        return request_json("POST", "/cards/collection", body={"identifiers": collection_identifiers(args)})

    if args.command == "get":
        return request_json("GET", args.path, params=parse_param(args.param))

    raise SystemExit(f"Unknown command: {args.command}")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        payload = run(args)
        print_payload(payload, args.format, limit=getattr(args, "limit", None))
        return 0
    except ScryfallError as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

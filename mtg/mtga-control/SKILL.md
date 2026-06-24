---
name: mtga-control
description: Control Magic: The Gathering Arena (MTGA) on macOS with screenshots, coordinate clicks, keyboard input, and CoreGraphics fallback clicks. Use when the user asks Codex to operate MTGA, click Play, choose visible events, inspect the current MTGA screen, enter matchmaking, or interact with MTGA UI that does not expose useful accessibility elements.
---

# MTGA Control

## Overview

Operate MTGA through the `computer-use` MCP when possible, then fall back to a CoreGraphics click script when MTGA shows hover state but ignores synthetic accessibility clicks.

MTGA usually exposes only the native macOS window controls through accessibility. Treat screenshots as the source of truth and use coordinates.

## Workflow

1. Start with `mcp__computer_use.get_app_state` for app `com.wizards.mtga`.
2. Read the screenshot returned by the tool and identify the target visually.
3. For cards in hand, use drag-and-drop toward the battlefield; do not rely on click-to-play.
4. Try `mcp__computer_use.click` at the screenshot coordinate when the interaction is a button, target, menu, or other low-risk click.
5. If the cursor visibly hovers the target but MTGA does not activate it, use `scripts/cg-click-mtga.swift` with the same window-relative coordinate.
5. Re-run `get_app_state` after each meaningful action to confirm the screen changed.

Use the MTGA bundle id `com.wizards.mtga`. If the app is not listed or not running, use `mcp__computer_use.list_apps` to discover the exact app name/path before interacting.

## Playing Cards In Game

To play a land or cast a card from hand, select the card, drag it from the hand toward the battlefield/table area, and release it. MTGA may only highlight or inspect a card when clicked; a plain click is not reliable for playing cards in this setup.

Use this pattern:

1. Get the current screenshot.
2. Estimate the center of the card in hand.
3. Drag from that card center to an open battlefield/table point.
4. Release and immediately re-read the screen.

After a spell enters target-selection mode, use clicks for targets, equipment attachments, modal choices, buttons, and confirmation prompts.

During live games, keep narration short and act quickly enough to avoid the rope. Prefer terse updates like `playing land`, `casting Cauldron`, `equipping Bow`, or `passing`.

## Coordinate Rules

`computer-use` screenshot coordinates are the coordinates to use with `mcp__computer_use.click`.

For CoreGraphics fallback, pass the same screenshot coordinate as a window-relative coordinate:

```bash
swift /path/to/mtga-control/scripts/cg-click-mtga.swift --relative 1158 700
```

The script finds the visible MTGA window, adds the window origin, activates MTGA, and posts a HID-level left mouse down/up event.

Use `--absolute` only when coordinates are already macOS screen coordinates:

```bash
swift /path/to/mtga-control/scripts/cg-click-mtga.swift --absolute 1249 770
```

## Known Useful Targets

For a visible MTGA window around `1280x748`, the home-screen Play button is near window-relative coordinate `1158,700`.

When Play opens the panel, the visible tabs may include `Events`, `Find Match`, and `Recently Played`. The exact event cards vary; inspect the screenshot before clicking a card or `Play`/`Resume`.

## Safety

Do not start paid events, spend currency, concede matches, craft cards, open packs, or submit deck/event choices unless the user explicitly asks for that exact action.

For ambiguous actions, report the visible options and ask which one to select.

## Script

Use `scripts/cg-click-mtga.swift` when MTGA ignores `computer-use` clicks. Escalated permissions may be required because the command posts system mouse events and interacts with another app.

# fortress-tui

**Terminal showcase for [fortress-engine](https://github.com/efirvida/fortress-engine) — a polished TUI that doubles as a developer reference for integrating the engine.**

Interactive fiction engines are headless: they parse commands, validate actions, and emit events, but they never paint a pixel. `fortress-tui` is a reference implementation of one possible presentation layer — a Textual-based TUI that subscribes to the engine's event bus and renders the game. It exists so developers can see exactly how a UI plugs into the engine, and use it as a starting point for their own.

Not every game needs this interface. Some worlds will want a minimal REPL, others a rich dashboard, others an AI-chat wrapper. This project is one concrete, working example: **a first step, not the destination.**

## Features

- **Multi-panel TUI** — narrative, live status, command input
- **Exploration map** — visited rooms, traversed passages, and the current position rendered from the macro graph and movement events
- **Scrollable narrative history** with per-event-type coloring
- **Live side panel** — current room, room items, inventory, weight, exits, turn counter
- **Input with history** (↑/↓) and verb autocomplete
- **World-aware commands** — the TUI reads the world's `vocabulary.yaml` for verb aliases; TUI-local commands (help, look, inventory) are loaded from the world vocabulary and fall back to a default catalog
- **Media-ready render layer** — text today; image and audio renderers designed in and ready for engine events that don't exist yet (see [Architecture](#architecture))
- **Internationalized UI** — the interface adapts to the world's declared language (`world.yaml → language`), not hardcoded strings
- **Dark/light themes** and a debug overlay (flags, raw events, graph state)

## Quickstart

Requirements: Python 3.11+

```bash
pip install -e ".[dev]"
fortress-tui --world worlds/demo-5rooms
```

Run the bundled `demo-5rooms` tutorial world: move through five rooms, pick up a rusty key and a kitchen knife, cut the vines, and escape.

## Usage

```
fortress-tui [--world <path>] [--theme dark|light]
```

| Command | Action |
|---------|--------|
| `fortress-tui --world worlds/demo-5rooms` | Run the bundled demo world |
| `fortress-tui --world ../fortaleza/worlds/fortaleza` | Run any fortress-engine world |

> **Language note:** the TUI is language-agnostic. The language of the
> interface and the available in-game verbs are defined by the world's
> `world.yaml → language` and its `vocabulary.yaml`. The bundled
> `demo-5rooms` world happens to be in Spanish; a world declared as
> `language: "en"` would surface English verbs and English UI strings.

The `demo-5rooms` world's vocabulary is defined in `worlds/demo-5rooms/shared/vocabulary.yaml`. For this Spanish-language world, the engine accepts these verbs:

| Command | Action | Defined in |
|---------|--------|-----------|
| `ir <dirección>` / `norte`, `sur`, `este`, `oeste` | Move between rooms | `vocabulary.yaml` (verbs + movement_verbs) |
| `mirar` / `leer <objeto>` | Describe the current room or an object | `vocabulary.yaml` (verbs) |
| `inventario` / `inv` | List carried items | `vocabulary.yaml` (verbs) |
| `coger <objeto>` / `tomar` / `agarrar` | Take an item | `vocabulary.yaml` (verbs) |
| `ayuda` | Show TUI command help | TUI default catalog (overridable in world vocabulary) |

**In a world with `language: "en"`**, the vocabulary would declare English verb groups (e.g. `go`, `look`, `take`, `inventory`) and the TUI would load its English UI string catalog — no TUI code change required.

## Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                           fortress-tui                            │
│                                                                │
│  ┌─────────────────┐      ┌────────────────────────────────┐  │
│  │   engine_bridge  │      │  render layer (media-ready)    │  │
│  │                  │      │  ┌───────────┐ ┌────────────┐  │  │
│  │  builds engine,  │──────▶│  text       │ │ image      │  │  │
│  │  subscribes to   │events│  renderer   │ │ renderer   │  │  │
│  │  EventBus        │      │  (active)   │ │ (designed) │  │  │
│  └────────┬─────────┘      │  ┌───────────┐ ┌────────────┐  │  │
│           │                │  │ audio     │ │  ...       │  │  │
│  ┌────────▼─────────┐      │  │ backend   │ │            │  │  │
│  │  Textual widgets  │      │  │ (noop)    │ │            │  │  │
│  │  narrative/status │◀────┘  └───────────┘ └────────────┘  │  │
│  │  /input           │      └────────────────────────────────┘  │
│  └────────┬─────────┘                                           │
│           │ execute_turn(text)                                  │
│  ┌────────▼─────────┐                                           │
│  │  fortress-engine  │  (headless — graph engine, event bus)    │
│  └──────────────────┘                                           │
└──────────────────────────────────────────────────────────────────┘
```

```
src/fortress_tui/
├── app.py               # Textual App entrypoint
├── engine_bridge.py     # Builds engine, subscribes to EventBus → render layer
├── commands.py          # TUI command dispatch: world-vocabulary verbs + TUI-local fallback (help/look/inventory)
├── i18n.py              # UI string catalog keyed by world language (fallback when unsupported)
├── theme.py             # Textual CSS themes (dark/light)
├── render/
│   ├── renderer.py      # Media dispatch: event → text/image/audio renderer
│   ├── text_renderer.py # Active: narration events → narrative panel
│   ├── image_renderer.py# Designed: terminal protocols (kitty/sixel/unicode)
│   └── audio_backend.py # Designed: NoopAudioBackend default, external player optional
├── screens/
│   └── game.py          # Main game screen layout
└── widgets/
    ├── narrative.py     # Scrollable narrative panel
    ├── status.py        # Side status panel
    ├── map.py           # Exploration map: visited rooms, traversed passages, position
    └── command_input.py # Input with history + autocomplete
```

### Design principle: exploration map

The macro graph already knows every room and passage (`get_edges_from_anchor`), and the engine emits `entity_entered`/`entity_teleported` on every movement. The map widget tracks visited anchors from those events and renders the traversed world — visited rooms by name, known-but-unvisited passages as unexplored, and a marker at the protagonist's current position. The engine stays authoritative; the map is a pure projection of engine events and state.

### Design principle: internationalized UI

The TUI is **language-agnostic**, just like the engine. Every world declares its language in `world.yaml` (`language`, plus its `vocabulary.yaml` for verb aliases and `messages` for world-authored strings). The TUI:

- Loads its UI string catalog keyed by the world's declared language — panel titles, help text, welcome/error messages.
- If the world's language is not in the catalog yet, falls back to a default catalog without breaking.
- Routes TUI-local verbs (help/look/inventory) through the world's vocabulary when defined, falling back to a default catalog alias otherwise.

Engine narration text is already localized by the engine's narrator; the TUI never duplicates that responsibility.

### Design principle: media-ready render layer

The engine emits **events** — not text. Text is just one possible rendering of an event. The `engine_bridge` delivers raw events to a render layer that dispatches by event type and payload:

- **Today**: every narration event renders as text (the template narrator's output).
- **Tomorrow**: when the engine starts emitting events with image or audio references, the same dispatch routes them to the image renderer and audio backend — no bridge changes required.

This is the integration pattern the showcase exists to demonstrate: **UI listens to the engine, not the other way around.**

## Development

```bash
pip install -e ".[dev]"
pytest                # run the test suite
textual run --dev src/fortress_tui/app.py --world worlds/demo-5rooms  # dev mode
```

## Roadmap

The project is planned as epics tracked in [GitHub issues](https://github.com/efirvida/fortress-tui/issues):

| Epic | Issues | Status |
|------|--------|--------|
| `epic:fundacion` — repo, CI, docs | #1, #14 | In progress |
| `epic:core-tui` — playable TUI core | #2–#7, #15, #17 | Planned |
| `epic:media-ready` — image/audio render layer | #8–#10 | Designed |
| `epic:pulido` — themes, debug, autocomplete | #11–#13 | Planned |

## Related

- [fortress-engine](https://github.com/efirvida/fortress-engine) — the headless engine this TUI renders
- [La Fortaleza (1995)](https://github.com/merchise/fortaleza) — the classic text adventure that inspired the engine

## License

MIT

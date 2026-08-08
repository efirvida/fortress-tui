# fortress-tui — Agent Instructions

## Project identity

**Python 3.11+** terminal UI for the `fortress-engine` interactive fiction engine. `src/` layout (PEP 517), package name `fortress-tui`. Built on Textual.

This is a **reference implementation** of one possible presentation layer for the engine: it shows how a UI subscribes to the engine's event bus and renders the game. It is not the only interface the engine supports — it is a working example and a developer reference.

## Quick commands

```bash
pip install -e ".[dev]"          # dev install with pytest + textual-dev
pytest                           # run all tests (tests/ mirroring src/)
pytest -k "test_render"         # single test pattern
```

## Testing hard gate (MANDATORY — whole project)

This gate applies to **every slice, phase, or continuation**, before asking the user to continue, before committing, and before opening a PR:

1. Run branch coverage: `pytest --cov=src/fortress_tui --cov-branch --cov-report=term-missing -q`
2. **TOTAL coverage must be > 99%** (statements AND branches). Below that, STOP: write the missing tests first, re-run, then continue.
3. The only allowed uncovered item is provably unreachable dead code (e.g. a defensive `else` after an exhaustive dispatch), documented with a comment and justification. Anything else uncovered is a defect.
4. Tests must be **strict, not lax**: assert exact messages/values (no substring filters that pass when the validator is broken), cover failure branches (unknown event types, missing payload keys, unsupported languages, unrepresentable media), and assert exact dispatch outcomes (e.g. one narrative line per narration event, one renderer per event type).
5. **Integration is part of coverage**: the glue between engine bridge → render dispatch → widgets must be tested together, not only each module in isolation.
6. Tests belong in the same commit as the code they verify. Never commit code without green tests + coverage above the gate.

### Testability rule (CRITICAL for a TUI)

Textual widgets live inside the app event loop and are hard to test. **All logic that can be pure MUST be pure** and live outside widget classes:

- `engine_bridge.py` — builds the engine, subscribes to the EventBus, exposes events to the render layer. No Textual imports.
- `render/` — dispatch and renderers. Pure: event → output. No Textual imports except where a widget truly needs one.
- `commands.py` — command parsing/classification (TUI commands vs engine commands). Pure.
- `i18n.py` — string catalog lookup. Pure.
- `widgets/map.py` — the map model (visited rooms, traversed passages, position) is a pure dataclass fed by engine events; only the *rendering* of that model lives in the widget.

Widgets must remain thin: they consume pure models and render them. Business logic in widgets is a defect — it makes the coverage gate impossible.

## Architecture constants

These are hard design constraints. Do NOT violate them:

1. **UI listens to the engine, not the other way around.** The engine never knows a UI exists. All UI updates flow from EventBus events or from reading `WorldState`.
2. **Media-ready render layer.** The bridge delivers raw events to a render dispatch that decides the medium (text today; image/audio designed). Text is one rendering of an event, not the event itself. When the engine emits image/audio events, the same dispatch routes them — no bridge changes.
3. **Internationalized UI.** UI strings come from a catalog keyed by the world's declared language (`world.yaml → language`), with a fallback catalog when the language is unsupported. Engine narration is already localized by the engine's narrator — the TUI never duplicates that.
4. **Engine stays authoritative.** State panels and the map are pure projections of `WorldState` and engine events. The TUI never mutates engine state except through `TurnOrchestrator.execute_turn(text)`.
5. **Synchronous, single-threaded.** The engine is synchronous; the TUI adapts to it. No async engine calls.

## Code conventions

- **Code identifiers (classes, methods, variables) in English.** UI copy is internationalized (see i18n); never hardcode UI strings.
- **Spanish-neutral register for es catalogs** (usted, not voseo) unless the world or user explicitly requests another register.
- **Thin widgets, pure logic.** See the Testability rule above.
- Keep the same module layout as the README architecture; rename only with justification.

## Dependencies

Core: `textual>=0.60.0`, `rich>=13.0`, `fortress-engine` (local path during development). Dev extras: `pytest>=8.0`, `pytest-cov>=5.0`, `textual-dev>=1.0`.

## What NOT to do

- Don't put engine integration inside a widget class.
- Don't hardcode UI strings — route them through the i18n catalog.
- Don't make the bridge Textual-aware (no imports of `textual` in bridge/render/commands/i18n).
- Don't mutate `WorldState` directly from the UI.
- Don't add async layers to bridge engine calls.

# fortress-showcase

Terminal showcase for [fortress-engine](https://github.com/efirvida/fortress-engine) — a polished TUI that doubles as a developer reference for integrating the engine.

## Features

- Polished multi-panel TUI (narrative, status, input)
- Scrollable narrative history with per-event-type coloring
- Live side panel: current anchor, room items, inventory, exits, turn counter
- Input with history (↑/↓) and verb autocomplete
- System commands: `mirar`, `inventario`, `ayuda`, `guardar`, `cargar`
- Debug toggle: flags, raw events, graph state
- Dark/light themes

## Quickstart

```bash
pip install -e ".[dev]"
fortress-showcase --world worlds/demo-5rooms
```

## Architecture

```
src/fortress_showcase/
├── app.py               # Textual App entrypoint
├── engine_bridge.py     # EventBus subscriber → widget updates, state → panels
├── commands.py          # System command handlers
├── theme.py             # Textual CSS themes
├── screens/
│   └── game.py          # Main game screen layout
└── widgets/
    ├── narrative.py     # Scrollable narrative panel
    ├── status.py        # Side status panel
    └── command_input.py # Input with history + autocomplete
```

## License

MIT

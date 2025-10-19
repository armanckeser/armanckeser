# PyCon Notes

## Data Handling
- Document assumptions, column meanings, and data sources in README
- Use xarray for metadata
- Use converters to convert columns to Python objects
- openpyxl can manipulate Excel data (can't read functions that haven't been opened in Excel)

## Event Sourcing
- **Book**: Domain-Driven Design: Tackling Complexity in the Heart of Software - Eric Evans
- Value object vs entity:
  - Value object: change the value, change the identity
  - Entity: values don't change the identity (GeoLocation of different locations are still GeoLocations)
- Event storming: figure out events, constraints, and results
  - command by actor → constraint → event

## BeeWare
- **briefcase**: packaging/build tool
- **toga**: UI framework

## Free-Threaded Python
- Add `t` to end of Python distribution for no GIL
- When sharing data:
  - Make it immutable if possible
  - Make it write-once (cached property-like) if possible
  - Lock while reading and modify while not (like Rust)

## Design Pressure
- Talk by Hynek Schlawack: https://hynek.me/talks/

## Zen of Polymorphism
GitHub: https://github.com/bslatkin/pycon2025

Four approaches:
1. **One function**: Order of isinstance checks matter. Adding new approach requires duplicating entire match case.
2. **OOP**: Problem when adding new approach (pretty printing vs calculation). Makes you colocate one file per class instead of one file per feature. Organization is on the wrong axis. Scattered dependencies.
3. **Dynamic dispatch**: Use to isolate behavior and data when necessary. Maybe have the default be assert_never.
4. **Catamorphism**: Visitor pattern for recursive data structures. Create a traversal function and give it a function.

How to write your own: `kind = type(value).__mro__`

## TypeVarTuple and Unpack
- <3.12: needed TypeVar and subclass of Generic
- Now: `class Map[TK, TV]:`
- Can use tuple to have explicit ordering or unsized
- `TypeVarTuple` lets you have both (PEP-646)
- `*tuple[int, ...]`
- **StaticFrame** written by the speaker

## Exception Handling
Why exceptions: Learn what went wrong in traceback
- `raise from` and `raise from None`
- `err.add_note` - explain when this happened (useful in libraries)
- `ExceptionGroup` - when multiple things go wrong concurrently
- asyncio task groups group errors into `ExceptionGroup`s
- `except*` can catch an exception group or subset

## Dependency Injection
GitHub: https://github.com/ptomecek/pycon2025
- `validate_assignment=True`
- **Hydra**: framework for configuring complex applications
- Use BeforeValidator to make something Injectable (looks up from registry)
- Use `validate_call` to inject into random functions
- Use specific implementation to make auto-populating registry order independent
- **ccflow**

## Python Upgrades
Talk by Jason Fried
- Don't suppress warnings
- `PYTHONWARNINGS=once`
- Use libcst codemods, pyupgrade
- Don't touch `_private` methods

## Interesting Companies Mentioned
- **anvil** - Full stack platform
- **gel** - Smart-ish ORM

## Interruptible Extension Module
Talk by Zack Weinberg
- About CPython extensions
- CPython extensions don't usually use PyErr_CheckSignals, which causes bad keyboard interrupt handling

## Tech Debt
- Measure tech debt
- Recognize, track contributions, and celebrate wins
- Automate
- zipq barraiser github
- Quarterly goals - progress tracking - weighted priorities

## Programming Your Computer
- appscript
- blog.glyph.im
- Script Editor
- pygments
- Linux: pyatspi, accerciser, dasbus, D-feet
- Inspect, pywinauto, Ole for office
- quickmachotkey, global-hotkeys
- quickmacapp
- notify-py

## Color Theory for Data Viz
- Balance the weights, avoid loud mouths (red etc.)

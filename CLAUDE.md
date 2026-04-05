# CLAUDE.md

This repository contains a small local web app for tracking papers you have read.

## Stack

- Python 3
- FastAPI
- Jinja2 templates
- htmx
- SQLite via Python's standard `sqlite3`

## Files

- `app.py`: FastAPI app, routes, and SQLite access
- `templates/index.html`: single-page UI
- `templates/partials/paper_item.html`: partial for each paper card
- `requirements.txt`: Python dependencies

## Run

1. Create a virtual environment:
   `python3 -m venv .venv`
2. Activate it:
   `source .venv/bin/activate`
3. Install dependencies:
   `python3 -m pip install -r requirements.txt`
4. Start the app:
   `python3 -m uvicorn app:app --reload`
5. Open:
   `http://localhost:8000`

## Notes

- The SQLite database file is created automatically as `papers.db`.
- The app is meant for local single-user use only.

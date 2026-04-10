# CLAUDE.md

This repository contains a small local web app for tracking papers you have read.

## Stack

- Python 3
- FastAPI
- Jinja2 templates
- htmx 2.0.4 (loaded from CDN in `index.html`)
- SQLite via Python's standard `sqlite3`

## Files

- `app.py`: エントリポイント。FastAPIインスタンス生成・ルーター登録・startup hookのみ
- `db/connection.py`: `get_connection()`, `utc_now_iso()`, `DB_PATH`, `BASE_DIR`
- `db/migrations.py`: スキーマバージョン管理・マイグレーション処理、`init_db()`
- `db/papers.py`: papers テーブルの CRUD 操作（`list_papers`, `create_paper_record`, `get_paper`, `update_paper_memo`, `update_paper_tags`, `delete_paper_record`, `normalize_tags`, `list_all_tags`）
- `routers/papers.py`: FastAPI ルートハンドラ一式
- `static/css/style.css`: 全スタイル定義
- `static/js/main.js`: textarea 自動リサイズ・折りたたみトグルの JS
- `templates/index.html`: outer HTML shell; includes `partials/page_content.html`
- `templates/partials/page_content.html`: full page body (add-paper form + paper list); htmx target `#page`
- `templates/partials/paper_item.html`: single paper card; htmx target `#paper-{{ paper.id }}`
- `requirements.txt`: Python dependencies (pin versions when adding)

## Database schema

Table: `papers`

| Column       | Type    | Notes                        |
|--------------|---------|------------------------------|
| `id`         | INTEGER | PK, autoincrement            |
| `title`      | TEXT    | required, non-empty          |
| `authors`    | TEXT    | optional, default `''`       |
| `url`        | TEXT    | optional, default `''`       |
| `memo`       | TEXT    | optional, default `''`       |
| `created_at` | TEXT    | UTC ISO-8601, set on insert  |
| `updated_at` | TEXT    | UTC ISO-8601, updated on edit|

`papers.db` is created automatically at startup via `init_db()`.

## API routes

| Method | Path                        | Description                          | htmx response          |
|--------|-----------------------------|--------------------------------------|------------------------|
| GET    | `/`                         | Render full page                     | full HTML              |
| POST   | `/papers`                   | Create paper (form: title, authors, url, memo) | `partials/page_content.html` (swaps `#page`) |
| POST   | `/papers/{id}/memo`         | Update memo (form: memo)             | `partials/paper_item.html` (swaps `#paper-{id}`) |
| POST   | `/papers/{id}/delete`       | Delete paper                         | empty `HTMLResponse("")` (removes `#paper-{id}`) |

Validation: `title` must be non-empty; returns 422 with `error` in context otherwise.

## Template context variables

- `page_content.html`: `papers` (list of dicts), `error` (str), `form_data` (dict with keys `title`, `authors`, `url`, `memo`)
- `paper_item.html`: `paper` (dict with all DB columns), `saved` (bool, show confirmation message)

## Coding conventions

- All DB access goes through helper functions in `app.py` (`list_papers`, `create_paper_record`, `get_paper`, `update_paper_memo`, `delete_paper_record`). Do not inline SQL in route handlers.
- Timestamps: always use `utc_now_iso()` (returns UTC ISO-8601 string).
- Routes return `HTMLResponse` / `TemplateResponse`; no JSON endpoints.
- No test suite exists. Verify changes manually by running the app.
- UI text is in Japanese; keep new UI strings in Japanese.
- Do not add external CSS/JS frameworks. Styles live in `static/css/style.css`; JS lives in `static/js/main.js`.

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

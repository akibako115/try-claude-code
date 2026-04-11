# Paper Notes

読んだ論文を記録・管理する Web アプリです。

FastAPI による JSON REST API バックエンドと、SQLAlchemy ORM による多ユーザー対応・PostgreSQL 対応を実装しています。

## できること

- ユーザー登録・ログイン（JWT 認証）
- 論文の登録・一覧表示・削除
- 論文ごとのメモ更新・タグ管理
- タグによるフィルタリング
- OpenAI API を使ったメモの自動生成（オプション）

## 使用技術

- Python 3
- FastAPI
- SQLAlchemy 2.0 (ORM)
- Alembic (マイグレーション)
- PostgreSQL / SQLite
- JWT 認証 (`python-jose`)

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

`.env` ファイルを作成します。

```bash
cp .env.example .env
# SECRET_KEY を安全な値に変更してください
```

## 起動方法

```bash
python3 -m uvicorn app:app --reload
```

起動時に Alembic マイグレーションが自動実行されます。

API ドキュメント: `http://localhost:8000/api/docs`

## データベース設定

デフォルトは SQLite（`papers.db`）です。PostgreSQL を使う場合は `.env` を編集します。

```text
DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/paper_notes
```

```bash
brew services start postgresql
createdb paper_notes
```

## API エンドポイント

| Method | Path | 説明 |
|--------|------|------|
| POST | `/api/v1/auth/register` | ユーザー登録 |
| POST | `/api/v1/auth/login` | ログイン・トークン取得 |
| GET | `/api/v1/auth/me` | 認証ユーザー情報 |
| GET | `/api/v1/papers/` | 論文一覧（?tag= でフィルタ） |
| POST | `/api/v1/papers/` | 論文作成 |
| GET | `/api/v1/papers/{id}` | 論文取得 |
| PATCH | `/api/v1/papers/{id}/memo` | メモ更新 |
| PATCH | `/api/v1/papers/{id}/tags` | タグ更新 |
| DELETE | `/api/v1/papers/{id}` | 論文削除 |

## 主要ディレクトリ

```
app.py            # FastAPI アプリ・起動時マイグレーション
config.py         # pydantic-settings による環境変数管理
models/           # SQLAlchemy ORM モデル
schemas/          # Pydantic スキーマ
repositories/     # DB アクセス層
services/         # ビジネスロジック層
routers/          # ルートハンドラ
alembic/          # マイグレーション
```

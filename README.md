# Paper Notes

読んだ論文を記録・管理する Web アプリです。

FastAPI JSON REST API バックエンド + React (Vite + TypeScript) SPA フロントエンドで構成しています。

## できること

- ユーザー登録・ログイン（JWT 認証）
- 論文の登録・一覧表示・削除
- 論文ごとのメモ更新・タグ管理
- タグによるフィルタリング
- OpenAI API を使ったメモの自動生成（オプション）

## 使用技術

**バックエンド**
- Python 3 / FastAPI
- SQLAlchemy 2.0 / Alembic
- PostgreSQL / SQLite
- JWT 認証 (`python-jose`)

**フロントエンド**
- React 18 + TypeScript
- Vite
- TanStack Query v5
- axios
- react-router-dom v7

## セットアップ

### バックエンド

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# SECRET_KEY を安全な値に変更してください
```

### フロントエンド

```bash
cd frontend
npm install
```

## 起動方法

### 開発時（バックエンド + フロントエンド別々に起動）

```bash
# バックエンド（ポート 8000）
python3 -m uvicorn app:app --reload

# フロントエンド（別ターミナル、ポート 5173）
cd frontend && npm run dev
```

起動後: `http://localhost:5173`

### 本番ビルド

```bash
cd frontend && npm run build
python3 -m uvicorn app:app
```

`frontend/dist` が存在する場合、バックエンドが SPA を配信します。起動後: `http://localhost:8000`

## データベース設定

デフォルトは SQLite（`papers.db`）です。PostgreSQL を使う場合は `.env` を編集します。

```text
DATABASE_URL=postgresql+psycopg2://<user>:<password>@localhost:5432/paper_notes
```

```bash
brew services start postgresql
createdb paper_notes
```

起動時に Alembic マイグレーションが自動実行されます。

## 主要ディレクトリ

```
app.py            # FastAPI アプリ・起動時マイグレーション
config.py         # 環境変数管理
models/           # SQLAlchemy ORM モデル
schemas/          # Pydantic スキーマ
repositories/     # DB アクセス層
services/         # ビジネスロジック層
routers/          # API ルートハンドラ
alembic/          # マイグレーション
frontend/
  src/
    api/          # axios クライアント・API 呼び出し
    context/      # AuthContext（JWT・ログイン状態管理）
    hooks/        # TanStack Query フック
    components/   # UI コンポーネント
    pages/        # ページコンポーネント
```

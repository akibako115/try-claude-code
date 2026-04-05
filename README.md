# Paper Notes

読んだ論文をローカルで手早く記録するための、最小構成の Web アプリです。

FastAPI でサーバを立て、SQLite に保存し、UI は HTML と `htmx` で軽く構成しています。

## できること

- 論文の登録
- 登録済み論文の一覧表示
- 論文ごとのメモ更新
- 論文の削除

## 使用技術

- Python 3
- FastAPI
- Jinja2
- htmx
- SQLite (`sqlite3`)

## セットアップ

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## 起動方法

```bash
python3 -m uvicorn app:app --reload
```

起動後、ブラウザで以下を開きます。

```text
http://localhost:8000
```

## 保存先

- SQLite ファイルはリポジトリ直下の `papers.db` に自動作成されます
- テーブルは初回起動時に自動作成されます

## 主要ファイル

- `app.py`: FastAPI アプリ本体、ルーティング、SQLite 操作
- `templates/index.html`: 画面全体のテンプレート
- `templates/partials/page_content.html`: ページ本体の部分テンプレート
- `templates/partials/paper_item.html`: 論文カードの部分テンプレート
- `requirements.txt`: 依存パッケージ

## 動作確認

以下を確認済みです。

- `GET /` でトップページが `200 OK` を返す
- 初回アクセス時に `papers.db` と `papers` テーブルが作成される
- 論文登録エンドポイントが HTML を返し、一覧に反映される
- `TestClient` による登録、バリデーション、メモ更新、削除の確認

## 補足

- 単一ユーザのローカル利用を想定しています
- 認証、検索、タグ、書誌情報の自動取得は入っていません

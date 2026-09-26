# 案件管理サービス (Flask)

案件情報の管理を行うマイクロサービス

## ディレクトリ構成

```
project-service/
├── app.py              # Flaskアプリケーション
├── migrations/         # DBマイグレーション (Flask-Migrate / Alembic)
├── requirements.txt    # Python依存関係
├── Dockerfile         # Dockerイメージ定義
├── .dockerignore      # Docker除外ファイル
├── .gitignore         # Git除外ファイル
└── README.md          # このファイル
```

## セットアップ

### 1. 仮想環境の作成

```powershell
# 仮想環境作成
python -m venv venv

# 仮想環境有効化 (Windows)
venv\Scripts\activate
```

### 2. 依存関係のインストール

```powershell
pip install -r requirements.txt
```

### 3. ローカルで実行

```powershell
# サーバー起動
python app.py
```

ブラウザで http://localhost:8002 にアクセス

### 4. Dockerで実行

```powershell
# イメージをビルド
docker build -t project-service .

# コンテナを起動
docker run -p 8002:8002 project-service
```

## API エンドポイント

- `GET /` - ルートエンドポイント
- `GET /health` - ヘルスチェック
- `GET /api/projects` - 案件一覧取得
- `POST /api/projects` - 案件作成
- `GET /api/projects/{id}` - 案件詳細取得

### 案件新規登録 `POST /api/projects`

| 項目 | キー | 必須 | 制約 |
|------|------|------|------|
| 担当営業 | `sales_rep` | ○ | 100文字以内 |
| 案件名 | `title` | ○ | 200文字以内 |
| 案件概要 | `description` | ○ | - |

```powershell
curl.exe -X POST http://localhost:8002/api/projects `
  -H "Content-Type: application/json" `
  -d '{\"sales_rep\": \"山田\", \"title\": \"Webアプリ開発\", \"description\": \"React + Flaskでの開発\"}'
```

- 成功時: `201` と登録した案件（`id`, `created_at` を含む）
- 入力エラー時: `400` と `errors`（項目ごとのエラーメッセージ）

`projects` テーブルは起動時のマイグレーションで自動作成されます（下記「データベースマイグレーション」参照）。

## 開発

### 依存関係の追加

```powershell
pip install パッケージ名
pip freeze > requirements.txt
```

### データベースマイグレーション

Flask-Migrate (Alembic) でテーブル定義を管理しています。
`python app.py` で起動すると、サーバー起動前に `migrations/` の未適用マイグレーションが自動で適用されます。
k8s で複数 Pod が同時に起動しても、PostgreSQL の advisory lock により 1 Pod ずつ実行されるため競合しません。

モデル (`app.py`) を変更したときは、マイグレーションファイルを生成してコミットしてください。

```powershell
$env:FLASK_APP = "app.py"
flask db migrate -m "変更内容"   # migrations/versions/ にファイルが生成される（内容を確認すること）
flask db upgrade                 # ローカルDBに適用
```

## Kubernetesデプロイ

詳細は `jobmatch-k8s` リポジトリを参照

# 案件管理サービス (Flask)

案件情報の管理を行うマイクロサービス

## ディレクトリ構成

```
project-service/
├── app.py              # Flaskアプリケーション
├── requirements.txt    # Python依存関係
├── Dockerfile         # Dockerイメージ定義
├── .dockerignore      # Docker除外ファイル
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

## 開発

### 依存関係の追加

```powershell
pip install パッケージ名
pip freeze > requirements.txt
```

### データベース接続（TODO）

SQLAlchemyを使ってPostgreSQLに接続する設定を追加予定

## Kubernetesデプロイ

詳細は `jobmatch-k8s` リポジトリを参照

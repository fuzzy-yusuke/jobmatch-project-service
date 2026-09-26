from datetime import datetime, timezone

from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from flask_migrate import Migrate, upgrade
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text


app = Flask(__name__)
CORS(app)  # CORS設定

# データベース設定
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/project_db"
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL
# Pod再起動やDB再起動後に切れたコネクションを使い回さないようにする
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {"pool_pre_ping": True}

# アプリケーション設定
app.config['JSON_AS_ASCII'] = False

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# マイグレーション排他用のPostgreSQL advisory lockのキー（任意の固定値）
MIGRATION_LOCK_KEY = 8002

# 入力項目の最大文字数
SALES_REP_MAX_LENGTH = 100
TITLE_MAX_LENGTH = 200


class Project(db.Model):
    """案件"""
    __tablename__ = "projects"

    id = db.Column(db.Integer, primary_key=True)
    sales_rep = db.Column(db.String(SALES_REP_MAX_LENGTH), nullable=False)  # 担当営業
    title = db.Column(db.String(TITLE_MAX_LENGTH), nullable=False)  # 案件名
    description = db.Column(db.Text, nullable=False)  # 案件概要
    created_at = db.Column(
        db.DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "sales_rep": self.sales_rep,
            "title": self.title,
            "description": self.description,
            "created_at": self.created_at.isoformat(),
        }


def validate_project(data):
    """案件登録の入力チェック。エラーがあれば {項目名: メッセージ} を返す"""
    errors = {}
    rules = [
        ("sales_rep", "担当営業", SALES_REP_MAX_LENGTH),
        ("title", "案件名", TITLE_MAX_LENGTH),
        ("description", "案件概要", None),
    ]
    for field, label, max_length in rules:
        value = data.get(field)
        if not isinstance(value, str) or not value.strip():
            errors[field] = f"{label}は必須です"
        elif max_length and len(value.strip()) > max_length:
            errors[field] = f"{label}は{max_length}文字以内で入力してください"
    return errors


def run_migrations():
    """起動時にDBを最新のマイグレーションまで更新する

    k8sでは複数Podが同時に起動するため、PostgreSQLのadvisory lockで
    マイグレーションを1Podずつ直列に実行する
    """
    with app.app_context():
        if db.engine.dialect.name != "postgresql":
            upgrade()
            return
        with db.engine.connect() as conn:
            conn.execute(text("SELECT pg_advisory_lock(:key)"), {"key": MIGRATION_LOCK_KEY})
            try:
                upgrade()
            finally:
                conn.execute(text("SELECT pg_advisory_unlock(:key)"), {"key": MIGRATION_LOCK_KEY})


@app.route('/')
def root():
    return jsonify({
        "message": "案件管理サービスへようこそ",
        "service": "project-service"
    })


@app.route('/health')
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "project-service"
    })


@app.route('/api/projects', methods=['GET'])
def get_projects():
    """案件一覧を取得"""
    projects = Project.query.order_by(Project.id.desc()).all()
    return jsonify({"projects": [p.to_dict() for p in projects]})


@app.route('/api/projects', methods=['POST'])
def create_project():
    """新しい案件を作成"""
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({"message": "リクエストボディはJSONで指定してください"}), 400

    errors = validate_project(data)
    if errors:
        return jsonify({"message": "入力内容に誤りがあります", "errors": errors}), 400

    project = Project(
        sales_rep=data["sales_rep"].strip(),
        title=data["title"].strip(),
        description=data["description"].strip(),
    )
    db.session.add(project)
    db.session.commit()

    return jsonify({
        "message": "案件が作成されました",
        "project": project.to_dict()
    }), 201


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """案件詳細を取得"""
    project = db.session.get(Project, project_id)
    if project is None:
        return jsonify({"message": "案件が見つかりません"}), 404
    return jsonify({"project": project.to_dict()})


if __name__ == '__main__':
    run_migrations()
    # docker-compose / k8s の DEBUG 環境変数に合わせる
    debug = os.getenv("DEBUG", "True").lower() == "true"
    app.run(host='0.0.0.0', port=8002, debug=debug)

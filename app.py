from flask import Flask, jsonify, request
from flask_cors import CORS
import os
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)
CORS(app)  # CORS設定

# データベース設定
DATABASE_URL = os.getenv(
    "DATABASE_URL", "postgresql://user:password@localhost:5432/project_db"
)
app.config["SQLALCHEMY_DATABASE_URI"] = DATABASE_URL

# アプリケーション設定
app.config['JSON_AS_ASCII'] = False


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
    # TODO: データベースから取得
    projects = [
        {
            "id": 1,
            "title": "Webアプリケーション開発",
            "company_id": 1,
            "description": "React + Node.jsでのWebアプリ開発",
            "status": "募集中"
        },
        {
            "id": 2,
            "title": "モバイルアプリ開発",
            "company_id": 2,
            "description": "Flutter でのモバイルアプリ開発",
            "status": "進行中"
        }
    ]
    return jsonify({"projects": projects})


@app.route('/api/projects', methods=['POST'])
def create_project():
    """新しい案件を作成"""
    data = request.get_json()
    # TODO: データベースに保存
    return jsonify({
        "message": "案件が作成されました",
        "project": data
    }), 201


@app.route('/api/projects/<int:project_id>', methods=['GET'])
def get_project(project_id):
    """案件詳細を取得"""
    # TODO: データベースから取得
    project = {
        "id": project_id,
        "title": "サンプル案件",
        "company_id": 1,
        "description": "案件の詳細情報",
        "status": "募集中"
    }
    return jsonify({"project": project})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8002, debug=True)

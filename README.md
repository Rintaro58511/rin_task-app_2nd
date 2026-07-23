# タスク管理アプリケーション (Task Management App)

ログイン認証を備えた、シンプルで直感的に操作できるタスク管理Webアプリケーションです。  
ユーザーごとのタスク追加・編集・削除・ステータス変更や、期限・ステータス順でのソート・検索機能を備えています。

---

## 🛠 使用技術 (Tech Stack)

### バックエンド (Backend)
- **Python** 3.11+
- **FastAPI** (Webフレームワーク)
- **SQLAlchemy** (非同期ORM / `AsyncSession`)
- **Pydantic** (データバリデーション)
- **Pytest** (自動テスト)
- **PostgreSQL** (データベース)

### フロントエンド (Frontend)
- **HTML5 / CSS3**
- **JavaScript (ES6+)** (Fetch API)

### インフラ・環境 / 認証
- **Docker / Docker Compose** (コンテナ環境)
- **OAuth2 / JWT** (ユーザー認証)
- **Git / GitHub**

---

## 🚀 主な機能 (Features)

- **ユーザー管理**: サインアップ、ログイン（認証トークン発行）
- **タスクCRUD機能**:
  - タスクの新規作成（タイトル、詳細、期限、ステータス）
  - ユーザー所有タスクの一覧表示
  - タスク詳細の参照・編集・削除
- **絞り込み・並び替え**:
  - 期限（Deadline）順・ステータス（Status）順のソート
  - タスク名による部分一致検索（あいまい検索）
- **セキュリティ・権限管理**: 他ユーザーのタスク閲覧・編集を制御

---

## 💻 起動方法 (How to Run)

### 前提条件 (Prerequisites)

- [Docker](https://www.docker.com/) / [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- Docker Compose

### 1. リポジトリのクローン

```
git clone https://github.com/Rintaro58511/rin_task-app_2nd.git
cd rin_task-app_2nd
```

### 2. コンテナの起動

```
docker compose up -d --build
```

### 3. 動作確認

起動後、ブラウザで以下のURLにアクセスします。

Webアプリ / API: http://localhost:5500

APIドキュメント (Swagger UI): http://localhost:8002/docs


### 4. コンテナの停止

```
docker compose down
```

### 📄 ディレクトリ構造 (Directory Structure)
```
.
├── Dockerfile
├── README.md
├── docker-compose.yml
├── requirements.txt
├── app/
│   ├── cruds/            # DB操作ロジック (SQLAlchemy)
│   │   ├── tasks.py
│   │   └── user.py
│   ├── frontapp/         # フロントエンド画面・スクリプト
│   │   ├── login.html
│   │   ├── login.js
│   │   ├── signup.html
│   │   ├── signup.js
│   │   ├── task_list.html
│   │   └── task_list.js
│   ├── models/           # DBモデル定義
│   │   ├── tasks.py
│   │   └── user.py
│   ├── routers/          # APIエンドポイント定義 (FastAPI)
│   │   ├── tasks.py
│   │   └── user.py
│   ├── schemas/          # Pydanticスキーマ定義
│   │   ├── auth.py
│   │   ├── tasks.py
│   │   └── user.py
│   ├── db.py             # DB接続設定
│   ├── enums.py          # 定数・Enum定義
│   ├── init_database.py  # DB初期化処理
│   └── main.py           # アプリケーションエントリーポイント
└── tests/                # テストコード (Pytest)
    ├── task_router/      # タスクAPI用テスト
    │   ├── test_create_task.py
    │   ├── test_delete_task.py
    │   ├── test_get_tasks.py
    │   └── test_search_task.py
    ├── test_task_crud.py # CRUD・認証用テスト
    ├── test_user_crud.py
    ├── test_user_login.py
    ├── test_user_me.py
    └── test_user_signup.py
```

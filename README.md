# Task Management App

FastAPI / PostgreSQL を中心に構築した、ユーザー認証付きのタスク管理 Web
アプリケーションです。

タスクの CRUD、進捗管理、検索・ソート、サブタスク管理に加え、AWS
上への本番デプロイと GitHub Actions による CI/CD まで実装しています。

**公開URL:** https://d25ee7cqp3i4lf.cloudfront.net/

------------------------------------------------------------------------

## Features

-   ユーザー登録・ログイン
-   OAuth2 / JWT を利用した認証
-   ユーザー単位でのタスク管理
-   タスクの作成・取得・更新・削除
-   タスクのステータス・進捗率・コメント管理
-   タスク名による検索
-   期限・ステータスによるソート
-   サブタスクの作成・更新・削除
-   他ユーザーのタスクへのアクセス制御
-   Pytest による Unit / Connection Test + Coverage の自動テスト
-   GitHub Actions によるバックエンド・フロントエンドの自動デプロイ

------------------------------------------------------------------------

## Tech Stack

  Category             Technology
  -------------------- -----------------------------------------------------
  Backend              Python 3.13 / FastAPI
  ORM                  SQLAlchemy (AsyncSession)
  Validation / Settings    Pydantic / pydantic-settings
  Database / Migration     PostgreSQL / Alembic
  Authentication       OAuth2 / JWT
  Frontend             HTML / CSS / JavaScript (Fetch API)
  Test                 Pytest / pytest-anyio / HTTPX / pytest-cov
  Container            Docker / Docker Compose
  Cloud                AWS CloudFront / S3 / ALB / ECS Fargate / ECR / RDS
  CI/CD                GitHub Actions
  AWS Authentication   GitHub Actions OIDC / IAM Role
  Code Quality         Ruff Lint/Formatter

------------------------------------------------------------------------

## Architecture

本番環境では、フロントエンドの静的ファイルを S3 に配置し、CloudFront
をエントリーポイントとして配信しています。 バックエンドは Docker
コンテナとして ECS Fargate 上で稼働し、ALB
経由でアクセスします。データベースには RDS for PostgreSQL
を使用しています。

``` mermaid
flowchart LR
    User[User / Browser]

    subgraph AWS
        CF[CloudFront]
        S3[S3<br/>Frontend]
        ALB[Application Load Balancer]
        ECS[ECS Fargate<br/>FastAPI]
        RDS[(RDS<br/>PostgreSQL)]
        ECR[ECR]
    end

    User -->|HTTPS| CF
    CF -->|Static files| S3
    CF -->|API requests| ALB
    ALB --> ECS
    ECS --> RDS
    ECR --> ECS
```

### AWS services

-   **CloudFront**: フロントエンド配信と API
    アクセスのエントリーポイント
-   **S3**: HTML / CSS / JavaScript の静的ファイルを配置
-   **ALB**: API リクエストを ECS
    タスクへルーティングし、ヘルスチェックを実施
-   **ECS Fargate**: FastAPI の Docker コンテナを実行
-   **ECR**: 本番用 Docker イメージを保存
-   **RDS for PostgreSQL**: 本番データを永続化
-   **IAM / OIDC**: GitHub Actions から AWS へ長期 Access Key
    を保存せず認証

------------------------------------------------------------------------

## CI/CD

### Backend

`main` ブランチへの push を契機に GitHub Actions を実行します。

``` mermaid
flowchart LR
    Push[Push to main]
    TestDB[(PostgreSQL Test DB)]
    Ruff[linter/formatter]
    Pytest[Pytest]
    AlembicTest["Migration Test<br/>upgrade → downgrade → upgrade"]
    Build[Docker Buildx<br/>linux/arm64]
    ECR[ECR]
    Migration["ECS one-off Task<br/>alembic upgrade head"]
    ECS[ECS Service Deploy]
    Health[ALB Health Check]

    Push --> TestDB
    TestDB --> Ruff
    Ruff --> Pytest
    Pytest --> AlembicTest
    AlembicTest -->|Success| Build
    AlembicTest -->|Failure| Stop[Stop]
    Build --> ECR
    ECR --> Migration
    Migration --> |Success| ECS
    Migration --> |Failure| Stop[Stop]
    ECS --> Health
```

1.  GitHub Actions 上にテスト用 PostgreSQL を起動
2.  RuffによるLint/Formatチェック
3.  Pytest を実行
4.  Alembicの upgrade → downgrade → upgrade を実行し、migrationの適用・ロールバック・再適用が正常に行えることを検証
5.  テスト成功時のみ Docker イメージをビルド
6.  Buildx / QEMU を利用して `linux/arm64` イメージを生成
7.  ECR へイメージを push
8. ECS Task Definition を更新
9. ECS one-off Taskで `alembic upgrade head` を実行
10. migration成功時のみECS Serviceへローリングデプロイ
11. ALBのヘルスチェックを通過後、デプロイ完了

GitHub Actions から AWS への認証には OIDC を利用し、AWS の長期 Access
Key / Secret Access Key を GitHub に保存しない構成にしています。

### Frontend

`app/frontapp/**` に変更がある場合のみフロントエンド用 Workflow
を実行します。

``` text
Push to main
    ↓
GitHub Actions
    ↓
S3 Sync
    ↓
CloudFront Invalidation
    ↓
Deploy Complete
```

------------------------------------------------------------------------

## Security

-   JWT による API 認証
-   ユーザー ID に基づくタスク所有者チェック
-   他ユーザーのタスクへのアクセス制御
-   CORS の許可 Origin を環境ごとに管理
-   ETag / If-Matchによる楽観的排他制御
-   RDS の PostgreSQL ポートをインターネットへ直接公開せず、ECS の
    Security Group からの通信に制限
-   GitHub Actions → AWS の認証に OIDC を使用
-   本番用 Secret / DB 接続情報をソースコードへ直接記述しない

------------------------------------------------------------------------

## Testing

Pytest / pytest-anyio / HTTPX を利用し、単体テストと結合テストを実装しています。

### Unit Test

Router・Service・CRUD 層を対象に、FastAPI の Dependency Override や
Mock / monkeypatch を利用して依存関係を分離し、各処理の分岐を検証しています。

主に以下をテストしています。

- ユーザー登録・ログイン・JWT認証
- Task / SubTask の CRUD
- 入力値のバリデーション
- 存在しないリソースへのアクセス
- 他ユーザーが所有するリソースへのアクセス制御
- ETag / If-Match の検証

### Connection Test

テスト用 PostgreSQL に接続し、実際の DB アクセスを含めた API の動作を検証しています。

単体テストでは確認できない以下のような処理を対象としています。

- Task / SubTask の CRUD と DB への反映
- ユーザーごとのリソースアクセス制御
- ETag / If-Match を利用した楽観的排他制御
- DB 更新後のデータ整合性

### Coverage

pytest-cov を利用して Branch Coverage を含むカバレッジを計測しています。

- Test Coverage: 99%
- Branch Coverage を有効化
- CI では Coverage が 95% 未満の場合にテストを失敗させるよう設定

GitHub Actions 上でもテスト用 PostgreSQL を起動してテストを実行し、
テストまたは Coverage の品質基準を満たさない場合は、本番デプロイへ進まない構成にしています。

------------------------------------------------------------------------

## Project Structure

``` text
.
├── .github/
│   └── workflows/            # GitHub Actions
├── app/
│   ├── alembic/              # Migration scripts
│   ├── alembic.ini           # Alembic configuration
│   ├── cruds/                # SQLAlchemyを利用したDB操作
│   ├── frontapp/             # HTML / CSS / JavaScript
│   ├── models/               # SQLAlchemy Model
│   ├── routers/              # FastAPI Router
│   ├── schemas/              # Pydantic Schema
│   ├── config.py             # 環境変数・アプリ設定
│   ├── db.py                 # DB Engine / Session設定
│   ├── enums.py              # Enum 定義
│   └── main.py               # FastAPI エントリーポイント
├── tests/                    # Pytest
├── Dockerfile
├── docker-compose.yml
├── docker-compose.prod.yml
├── requirements.txt
└── README.md
```

------------------------------------------------------------------------

## Migrationの運用

### 1. Alembic導入の背景

従来は初期化処理によってテーブルを作成していましたが、この方式ではDBスキーマの変更履歴を管理できず、
デプロイ時のスキーマ更新も手動で行う必要がありました。

そこでAlembicを導入し、DBスキーマの変更をmigration fileとしてバージョン管理する構成へ変更しました。

### 2. DB設定の共通化

開発・テスト・本番でDB接続用の環境変数名を統一し、pydantic-settings によって必須値や型を起動時に検証する構成にしました。

### 3. Alembicの非同期対応

AsyncEngine / asyncpg で接続し、AsyncConnection.run_sync() を介してAlembicのmigration処理を実行する構成にしました。

### 4. CI/CDへのmigration組み込み

アプリコンテナ起動時にmigrationを実行すると、複数のECS Taskが同時にmigrationを実行する可能性があるため、
Serviceとは分離したone-off Taskで実行しています。
Migrationが失敗した場合はECS Serviceの更新へ進まず、DBスキーマとアプリケーションの不整合を防ぐ構成にしています。

------------------------------------------------------------------------

## Design / Implementation Highlights

### 1. 非同期 DB アクセス

FastAPI と SQLAlchemy の `AsyncSession` を利用し、DB I/O
を非同期で扱う構成にしています。

### 2. Router / CRUD / Schema / Model の責務分離

API エンドポイント、DB 操作、入力・出力スキーマ、DB
モデルを分離し、変更箇所の影響範囲を抑えられる構成を意識しています。

### 3. ETag を利用したキャッシュ検証と楽観的排他制御

Task の `changed_time` をもとに ETag を生成し、
データ取得時のキャッシュ検証と更新時の競合検知に利用しています。

#### GET: If-None-Match による変更検知

Task取得時に ETag をレスポンスヘッダーとして返します。

クライアントから送信された `If-None-Match` と現在の ETag が一致する場合は、
Taskが更新されていないと判断し、`304 Not Modified` を返します。

Taskが更新され `changed_time` が変更されている場合は新しい ETag とともに
最新のTaskデータを返します。

#### PUT: If-Match による楽観的排他制御

複数のリクエストによる Lost Update を防ぐため、
更新時には `If-Match` と現在の ETag を比較します。

一致する場合のみ更新を許可し、一致しない場合は
`412 Precondition Failed` を返して最新データの再取得を要求します。

これらの動作については PostgreSQL を利用した結合テストを実装し、
Task更新後の ETag の変更や、古い ETag を利用した更新が
拒否されることを確認しています。


### 4. 認証だけでなく認可も実装

ログインできるかだけでなく、取得・更新・削除しようとしているタスクが認証ユーザー自身のものかを確認し、
他ユーザーのデータへアクセスできないようにしています。

### 5. Docker multi-stage build

Docker の multi-stage build
を利用し、開発環境と本番環境で必要な内容を分離しています。

### 6. CI/CD

100,000件のTaskデータを用いて EXPLAIN ANALYZE で検証した結果、
user_id のIndexによって対象クエリの実行時間が約4.76msから約0.50msへ短縮されました。
一方、deadline / task_progress は現在のクエリパターンではIndexが利用されなかったため、
不要なIndexは追加しない設計としました。

------------------------------------------------------------------------

## Problems Solved During Development

### CPU architecture mismatch

GitHub Actions で生成した Docker イメージと ECS Fargate の CPU
アーキテクチャが一致せず、次のエラーが発生しました。

``` text
exec /opt/venv/bin/uvicorn: exec format error
```

ECS を ARM64 で構成していたため、GitHub Actions に QEMU / Docker Buildx
を導入し、`linux/arm64` を明示してイメージを生成することで解決しました。

### Differences between local and CI environments

ローカル Docker では成功していたテストが GitHub Actions
上で失敗し、`PYTHONPATH` やテスト用 `SECRET_KEY`
などの環境差を発見しました。CI 上でも必要な環境変数と PostgreSQL
テスト環境を明示することで解決しました。

### Authentication / authorization tests

タスク所有者チェック追加後に既存テストとの不整合を検出しました。Dependency
Override
を利用して認証ユーザーを明示し、正常系・存在しないタスク・他ユーザーのタスクへのアクセスを
分けてテストするよう修正しました。

### Test database isolation

pytestが開発DBを参照していたため、drop_all() により開発DBのテーブルが削除されました。
開発用の app → db とテスト用の app-test → db-test を分離し、
pytestによるテーブル作成・削除が開発DBへ影響しない構成に変更することで解決しました。

### ECS / ALB Availability Zone mismatch

ECS Taskがap-northeast-1dに配置された一方、ALBではap-northeast-1a / 1cのみが有効だったため、
ECS Serviceの配置先をALBと同じAZに統一して解決しました。

------------------------------------------------------------------------

## Future Improvements

-   CloudFront / ALB 周辺のさらなるセキュリティ強化
-   ログ・監視・アラートの強化
-   フロントエンドのコンポーネント化・UI 改善

------------------------------------------------------------------------

## Repository

https://github.com/Rintaro58511/rin_task-app_2nd

# AI-Powered Task & Knowledge Management

## Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full design document.

## Prerequisites

- Python 3.11+
- MySQL 8.0+ with a `task_knowledge_db` database
- Node.js 20+ (for frontend)

## Backend Setup

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# Linux/macOS
source .venv/bin/activate

pip install -r requirements.txt
```

### Environment

Copy `.env.example` to `backend/.env` and fill in your credentials:

```
DATABASE_URL=mysql+pymysql://app_user:your_password@localhost:3306/task_knowledge_db
DB_HOST=localhost
DB_PORT=3306
DB_NAME=task_knowledge_db
DB_USER=app_user
DB_PASSWORD=your_password
JWT_SECRET=generate_with_openssl_rand_hex_32
JWT_ALGORITHM=HS256
JWT_EXPIRE_MINUTES=60
```

### Database

Create the MySQL database and a dedicated application user (do not use root):

```sql
CREATE DATABASE task_knowledge_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'app_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON task_knowledge_db.* TO 'app_user'@'localhost';
FLUSH PRIVILEGES;
```

### Migrations

```bash
cd backend
alembic upgrade head
```

### Seed

```bash
SEED_ADMIN_PASSWORD=AdminPass123! SEED_USER_PASSWORD=UserPass123! python seed.py
```

### Run

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

API docs: http://localhost:8000/docs

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

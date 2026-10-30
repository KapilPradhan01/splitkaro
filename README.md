# SplitKaro

An expense-splitting app for groups, with graph-based debt simplification that cuts down the number of payments needed to settle up.

## How It Works

Debts in a group form a graph: members are nodes, and "A owes B" is a directed edge. SplitKaro computes each member's net balance, then matches people who are owed money against people who owe money, producing the fewest practical transactions without changing anyone's net position.

## Tech Stack

FastAPI, PostgreSQL, SQLAlchemy, Alembic

## Setup

```bash
git clone https://github.com/KapilPradhan01/splitkaro.git
cd splitkaro
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
DATABASE_URL=postgresql://<user>:<password>@localhost:5432/splitkaro
```

Run migrations and start the server:

```bash
alembic upgrade head
uvicorn app.main:app --reload
```

API docs are available at `http://localhost:8000/docs`.

## Author

Kapil Pradhan ([@KapilPradhan01](https://github.com/KapilPradhan01))

# SplitKaro

An expense-splitting app for groups, with graph-based debt simplification that cuts down the number of payments needed to settle up.

## Features

- Track shared expenses within a group
- Calculate each member's net balance
- Simplify debts using a graph-based algorithm to minimize settlement transactions

## How It Works

Debts in a group form a graph: members are nodes, and "A owes B" is a directed edge. SplitKaro computes each member's net balance, then matches people who are owed money against people who owe money, producing the fewest practical transactions without changing anyone's net position.

### Example

Before simplification:

```
A owes B  500
B owes C  500
```

After simplification:

```
A pays C  500
```

B was only a middleman, so the debt chain collapses into a single payment. B's net balance is zero either way.

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

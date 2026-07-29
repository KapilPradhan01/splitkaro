from fastapi import FastAPI
from app.core.database import create_tables

# Import all models so Base knows about them
from app.models import user, groups, groupmembers, expense, split, settlement

app = FastAPI(
    title="SplitKaro API",
    description="India-first smart expense splitter",
    version="1.0.0"
)

@app.on_event("startup")
def startup():
    create_tables()
    print("✅ Tables created successfully!")

@app.get("/")
def root():
    return {"message": "Welcome to SplitKaro API"}
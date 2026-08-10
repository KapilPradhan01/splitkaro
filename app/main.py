from fastapi import FastAPI
from app.core.database import create_tables
from app.models import user, groups, groupmembers, expense, split, settlement
from app.api.routes import auth

app = FastAPI(
    title="SplitKaro API",
    description="India-first smart expense splitter",
    version="1.0.0"
)

# Register routes
app.include_router(auth.router)

@app.on_event("startup")
def startup():
    create_tables()
    print("✅ Tables created successfully!")

@app.get("/")
def root():
    return {"message": "Welcome to SplitKaro API"}
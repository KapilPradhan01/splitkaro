from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.expense import Expense
from app.models.split import Split
from app.models.groupmembers import GroupMember
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/expenses", tags=["Expenses"])


# ── REQUEST SCHEMAS ───────────────────────────────────────
class SplitInput(BaseModel):
    user_id: str
    amount: float


class CreateExpenseRequest(BaseModel):
    group_id: str
    paid_by: str
    amount: float
    description: str
    category: Optional[str] = "general"
    split_type: str = "equal"
    splits: Optional[List[SplitInput]] = None


# ── CREATE EXPENSE ────────────────────────────────────────
@router.post("/")
def create_expense(payload: CreateExpenseRequest, db: Session = Depends(get_db)):

    # Step 1: Verify payer is in the group
    member = db.query(GroupMember).filter(
        GroupMember.group_id == payload.group_id,
        GroupMember.user_id == payload.paid_by
    ).first()
    if not member:
        raise HTTPException(status_code=403, detail="User is not a member of this group")

    # Step 2: Get all group members for equal split
    all_members = db.query(GroupMember).filter(
        GroupMember.group_id == payload.group_id
    ).all()

    # Step 3: Create the expense
    expense = Expense(
        group_id=payload.group_id,
        paid_by=payload.paid_by,
        amount=payload.amount,
        description=payload.description,
        category=payload.category,
        split_type=payload.split_type,
    )
    db.add(expense)
    db.flush()

    # Step 4: Create splits based on split_type
    if payload.split_type == "equal":
        # Divide equally among all members
        share = round(payload.amount / len(all_members), 2)
        for i, member in enumerate(all_members):
            # Last person gets remainder to avoid rounding issues
            if i == len(all_members) - 1:
                amt = round(payload.amount - share * (len(all_members) - 1), 2)
            else:
                amt = share
            db.add(Split(
                expense_id=expense.id,
                user_id=member.user_id,
                amount_owed=amt
            ))

    elif payload.split_type == "exact":
        # Validate splits add up to total
        if not payload.splits:
            raise HTTPException(status_code=400, detail="Exact split requires splits list")
        total = sum(s.amount for s in payload.splits)
        if abs(total - payload.amount) > 0.01:
            raise HTTPException(status_code=400, detail=f"Splits total {total} doesn't match expense amount {payload.amount}")
        for s in payload.splits:
            db.add(Split(
                expense_id=expense.id,
                user_id=s.user_id,
                amount_owed=s.amount
            ))

    db.commit()
    db.refresh(expense)

    return {
        "message": "Expense added successfully",
        "expense": {
            "id": expense.id,
            "group_id": expense.group_id,
            "paid_by": expense.paid_by,
            "amount": expense.amount,
            "description": expense.description,
            "category": expense.category,
            "split_type": expense.split_type,
        }
    }


# ── GET GROUP EXPENSES ────────────────────────────────────
@router.get("/group/{group_id}")
def get_group_expenses(group_id: str, db: Session = Depends(get_db)):
    """Get all expenses for a group."""

    expenses = db.query(Expense).filter(
        Expense.group_id == group_id
    ).order_by(Expense.created_at.desc()).all()

    return {
        "group_id": group_id,
        "total_expenses": len(expenses),
        "expenses": [
            {
                "id": e.id,
                "paid_by": e.paid_by,
                "amount": e.amount,
                "description": e.description,
                "category": e.category,
                "split_type": e.split_type,
                "date": e.created_at
            }
            for e in expenses
        ]
    }


# ── GET BALANCES ──────────────────────────────────────────
@router.get("/balances/{group_id}")
def get_balances(group_id: str, db: Session = Depends(get_db)):
    """
    Calculate net balance for each member.
    Positive = person is owed money
    Negative = person owes money
    """

    # Get all members
    members = (
        db.query(User)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )

    # Initialize balances
    balances = {m.id: {"name": m.name, "balance": 0.0} for m in members}

    # Get all expenses
    expenses = db.query(Expense).filter(Expense.group_id == group_id).all()

    for expense in expenses:
        # Credit the person who paid
        if expense.paid_by in balances:
            balances[expense.paid_by]["balance"] += expense.amount

        # Debit each person their share
        splits = db.query(Split).filter(Split.expense_id == expense.id).all()
        for split in splits:
            if split.user_id in balances:
                balances[split.user_id]["balance"] -= split.amount_owed

    return {
        "group_id": group_id,
        "balances": [
            {
                "user_id": uid,
                "name": data["name"],
                "net_balance": round(data["balance"], 2),
                "status": "owed" if data["balance"] > 0.01
                         else "owes" if data["balance"] < -0.01
                         else "settled"
            }
            for uid, data in balances.items()
        ]
    }
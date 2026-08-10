from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.groups import Group
from app.models.groupmembers import GroupMember
from app.models.user import User
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter(prefix="/groups", tags=["Groups"])


# ── REQUEST SCHEMAS ───────────────────────────────────────
class CreateGroupRequest(BaseModel):
    name: str
    description: Optional[str] = None
    creator_id: str
    member_emails: List[str] = []


# ── CREATE GROUP ──────────────────────────────────────────
@router.post("/")
def create_group(payload: CreateGroupRequest, db: Session = Depends(get_db)):

    # Step 1: Verify creator exists
    creator = db.query(User).filter(User.id == payload.creator_id).first()
    if not creator:
        raise HTTPException(status_code=404, detail="Creator user not found")

    # Step 2: Create the group
    group = Group(
        name=payload.name,
        description=payload.description,
        created_by=payload.creator_id
    )
    db.add(group)
    db.flush()  # gets group.id without committing yet

    # Step 3: Add creator as admin member automatically
    creator_member = GroupMember(
        group_id=group.id,
        user_id=payload.creator_id,
        is_admin=True
    )
    db.add(creator_member)

    # Step 4: Add friends by email
    added = []
    not_found = []

    for email in payload.member_emails:
        user = db.query(User).filter(User.email == email).first()
        if user and user.id != payload.creator_id:
            db.add(GroupMember(
                group_id=group.id,
                user_id=user.id,
                is_admin=False
            ))
            added.append(email)
        else:
            not_found.append(email)

    db.commit()
    db.refresh(group)

    return {
        "message": "Group created successfully",
        "group": {
            "id": group.id,
            "name": group.name,
            "description": group.description,
            "created_by": group.created_by,
        },
        "members_added": added,
        "members_not_found": not_found
    }


# ── GET GROUP MEMBERS ─────────────────────────────────────
@router.get("/{group_id}/members")
def get_members(group_id: str, db: Session = Depends(get_db)):

    # Check group exists
    group = db.query(Group).filter(Group.id == group_id).first()
    if not group:
        raise HTTPException(status_code=404, detail="Group not found")

    # Get all members with their user details
    members = (
        db.query(User, GroupMember)
        .join(GroupMember, GroupMember.user_id == User.id)
        .filter(GroupMember.group_id == group_id)
        .all()
    )

    return {
        "group_id": group_id,
        "group_name": group.name,
        "members": [
            {
                "user_id": user.id,
                "name": user.name,
                "email": user.email,
                "upi_id": user.upi_id,
                "is_admin": member.is_admin,
                "joined_at": member.joined_at
            }
            for user, member in members
        ]
    }


# ── GET USER'S GROUPS ─────────────────────────────────────
@router.get("/user/{user_id}")
def get_user_groups(user_id: str, db: Session = Depends(get_db)):
    """Get all groups a user belongs to."""

    groups = (
        db.query(Group)
        .join(GroupMember, GroupMember.group_id == Group.id)
        .filter(GroupMember.user_id == user_id)
        .all()
    )

    return {
        "user_id": user_id,
        "groups": [
            {
                "id": g.id,
                "name": g.name,
                "description": g.description,
            }
            for g in groups
        ]
    }
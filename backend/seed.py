"""
Development seed script.

Usage:
    SEED_ADMIN_PASSWORD=<strong_password> SEED_USER_PASSWORD=<strong_password> \\
        python seed.py

Passwords must be provided via environment variables; they are never
hardcoded in source.
"""
import logging
import os
import sys

from sqlalchemy.orm import Session

from app.core.logging import configure_logging
from app.core.security import hash_password
from app.db.session import SessionLocal
from app.models.models import Role, RoleName, User

configure_logging()
logger = logging.getLogger(__name__)


def _get_required_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        logger.error("Environment variable %s is required for seeding but was not set", name)
        sys.exit(1)
    return value


def seed(db: Session) -> None:
    admin_password = _get_required_env("SEED_ADMIN_PASSWORD")
    user_password = _get_required_env("SEED_USER_PASSWORD")

    # Roles
    for role_name in (RoleName.ADMIN, RoleName.USER):
        exists = db.query(Role).filter_by(name=role_name.value).first()
        if not exists:
            db.add(Role(name=role_name.value))
            logger.info("Created role: %s", role_name.value)
    db.commit()

    admin_role = db.query(Role).filter_by(name=RoleName.ADMIN.value).one()
    user_role = db.query(Role).filter_by(name=RoleName.USER.value).one()

    # Seed users
    seed_users = [
        User(
            username="admin",
            email="admin@example.com",
            password_hash=hash_password(admin_password),
            role_id=admin_role.id,
            is_active=True,
        ),
        User(
            username="dev_user",
            email="dev@example.com",
            password_hash=hash_password(user_password),
            role_id=user_role.id,
            is_active=True,
        ),
    ]

    for user in seed_users:
        exists = db.query(User).filter_by(username=user.username).first()
        if not exists:
            db.add(user)
            logger.info("Created user: %s", user.username)
        else:
            logger.info("User already exists, skipping: %s", user.username)

    db.commit()
    logger.info("Seed complete")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
    finally:
        db.close()

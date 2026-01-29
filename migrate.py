#!/usr/bin/env python3
"""
Database migration script for Unified AceStream Platform

Usage:
    python migrate.py upgrade    # Apply all pending migrations
    python migrate.py downgrade  # Rollback last migration
    python migrate.py current    # Show current revision
    python migrate.py history    # Show migration history
"""
import sys
import os
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from alembic.config import Config
from alembic import command


def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg = Config("alembic.ini")
    return alembic_cfg


def upgrade():
    """Apply all pending migrations"""
    print("🔄 Applying database migrations...")
    alembic_cfg = get_alembic_config()
    command.upgrade(alembic_cfg, "head")
    print("✅ Migrations applied successfully!")


def downgrade():
    """Rollback last migration"""
    print("⚠️  Rolling back last migration...")
    alembic_cfg = get_alembic_config()
    command.downgrade(alembic_cfg, "-1")
    print("✅ Rollback completed!")


def current():
    """Show current database revision"""
    print("📍 Current database revision:")
    alembic_cfg = get_alembic_config()
    command.current(alembic_cfg)


def history():
    """Show migration history"""
    print("📜 Migration history:")
    alembic_cfg = get_alembic_config()
    command.history(alembic_cfg)


def stamp(revision="head"):
    """Stamp database with a specific revision without running migrations"""
    print(f"🏷️  Stamping database with revision: {revision}")
    alembic_cfg = get_alembic_config()
    command.stamp(alembic_cfg, revision)
    print("✅ Database stamped successfully!")


def main():
    """Main entry point"""
    if len(sys.argv) < 2:
        print("Usage: python migrate.py [upgrade|downgrade|current|history|stamp]")
        sys.exit(1)
    
    action = sys.argv[1].lower()
    
    if action == "upgrade":
        upgrade()
    elif action == "downgrade":
        downgrade()
    elif action == "current":
        current()
    elif action == "history":
        history()
    elif action == "stamp":
        revision = sys.argv[2] if len(sys.argv) > 2 else "head"
        stamp(revision)
    else:
        print(f"❌ Unknown action: {action}")
        print("Available actions: upgrade, downgrade, current, history, stamp")
        sys.exit(1)


if __name__ == "__main__":
    main()

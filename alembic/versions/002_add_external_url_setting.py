"""Add external_url setting

Revision ID: 002
Revises: 001
Create Date: 2026-01-25 21:36:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime


# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add external_url setting to settings table"""
    
    # Insert the external_url setting if it doesn't exist
    # Using raw SQL to avoid issues with ORM
    connection = op.get_bind()
    
    # Check if setting already exists
    result = connection.execute(
        sa.text("SELECT COUNT(*) FROM settings WHERE key = 'external_url'")
    ).scalar()
    
    if result == 0:
        # Insert the setting
        connection.execute(
            sa.text("""
                INSERT INTO settings (key, value, description, created_at, updated_at)
                VALUES (:key, :value, :description, :created_at, :updated_at)
            """),
            {
                'key': 'external_url',
                'value': '',
                'description': 'URL externa para acceso remoto (opcional, ej: http://mi-dominio.com:6880)',
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
        )


def downgrade() -> None:
    """Remove external_url setting from settings table"""
    
    connection = op.get_bind()
    connection.execute(
        sa.text("DELETE FROM settings WHERE key = 'external_url'")
    )

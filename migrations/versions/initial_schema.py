"""Initial schema

Revision ID: initial_schema
Revises: 
Create Date: 2024-01-01 00:00:00.000000
"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic
revision = 'initial_schema'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create recipes table
    op.create_table(
        'recipes',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('ingredients', sa.Text(), nullable=False),
        sa.Column('servings', sa.Integer(), nullable=False),
        sa.Column('categories', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_recipe_name', 'recipes', ['name'])
    op.create_index('idx_recipe_categories', 'recipes', ['categories'])

def downgrade():
    # Remove indexes
    op.drop_index('idx_recipe_categories')
    op.drop_index('idx_recipe_name')
    
    # Drop recipes table
    op.drop_table('recipes')
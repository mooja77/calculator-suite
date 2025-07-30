"""Global infrastructure tables

Revision ID: global_infrastructure
Revises: 
Create Date: 2024-01-15 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from datetime import date

# revision identifiers
revision = 'global_infrastructure'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create currencies table
    op.create_table('currencies',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=3), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('symbol', sa.String(length=10), nullable=False),
        sa.Column('decimal_places', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create exchange_rates table
    op.create_table('exchange_rates',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('base_currency', sa.String(length=3), nullable=False),
        sa.Column('target_currency', sa.String(length=3), nullable=False),
        sa.Column('rate', sa.Numeric(precision=15, scale=8), nullable=False),
        sa.Column('source', sa.String(length=50), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('base_currency', 'target_currency', name='_currency_pair')
    )
    
    # Create indexes for exchange_rates
    op.create_index('idx_exchange_rates_pair', 'exchange_rates', ['base_currency', 'target_currency'], unique=False)
    op.create_index('idx_exchange_rates_expires', 'exchange_rates', ['expires_at'], unique=False)
    
    # Create countries table
    op.create_table('countries',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('code', sa.String(length=2), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('currency_code', sa.String(length=3), nullable=False),
        sa.Column('decimal_separator', sa.String(length=1), nullable=True),
        sa.Column('thousands_separator', sa.String(length=1), nullable=True),
        sa.Column('date_format', sa.String(length=20), nullable=True),
        sa.Column('time_format', sa.String(length=20), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('language_code', sa.String(length=5), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('code')
    )
    
    # Create user_preferences table
    op.create_table('user_preferences',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.String(length=128), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=True),
        sa.Column('currency_code', sa.String(length=3), nullable=True),
        sa.Column('language_code', sa.String(length=5), nullable=True),
        sa.Column('decimal_separator', sa.String(length=1), nullable=True),
        sa.Column('thousands_separator', sa.String(length=1), nullable=True),
        sa.Column('date_format', sa.String(length=20), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=True),
        sa.Column('preferences_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index for user_preferences
    op.create_index('idx_user_preferences_session', 'user_preferences', ['session_id'], unique=False)
    
    # Create tax_rules table
    op.create_table('tax_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_code', sa.String(length=2), nullable=False),
        sa.Column('region_code', sa.String(length=10), nullable=True),
        sa.Column('tax_type', sa.String(length=50), nullable=False),
        sa.Column('rate', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('description', sa.String(length=200), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('effective_date', sa.Date(), nullable=False),
        sa.Column('expiry_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for tax_rules
    op.create_index('idx_tax_rules_location', 'tax_rules', ['country_code', 'region_code'], unique=False)
    op.create_index('idx_tax_rules_type', 'tax_rules', ['tax_type'], unique=False)
    op.create_index('idx_tax_rules_active', 'tax_rules', ['is_active', 'effective_date'], unique=False)

def downgrade():
    # Drop indexes first
    op.drop_index('idx_tax_rules_active', table_name='tax_rules')
    op.drop_index('idx_tax_rules_type', table_name='tax_rules')
    op.drop_index('idx_tax_rules_location', table_name='tax_rules')
    op.drop_index('idx_user_preferences_session', table_name='user_preferences')
    op.drop_index('idx_exchange_rates_expires', table_name='exchange_rates')
    op.drop_index('idx_exchange_rates_pair', table_name='exchange_rates')
    
    # Drop tables
    op.drop_table('tax_rules')
    op.drop_table('user_preferences')
    op.drop_table('countries')
    op.drop_table('exchange_rates')
    op.drop_table('currencies')
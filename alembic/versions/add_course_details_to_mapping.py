"""add course details to user course mapping

Revision ID: add_course_details_to_mapping
Revises: 
Create Date: 2024-03-19

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_course_details_to_mapping'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns
    op.add_column('user_course_mapping', sa.Column('course_name', sa.String(255), nullable=True))
    op.add_column('user_course_mapping', sa.Column('course_description', sa.String(1000), nullable=True))
    
    # Update existing rows with course details
    op.execute("""
        UPDATE user_course_mapping ucm
        JOIN courses c ON ucm.course_id = c.id
        SET ucm.course_name = c.name,
            ucm.course_description = c.description
    """)
    
    # Make columns not nullable after data migration
    op.alter_column('user_course_mapping', 'course_name',
                    existing_type=sa.String(255),
                    nullable=False)

def downgrade():
    op.drop_column('user_course_mapping', 'course_description')
    op.drop_column('user_course_mapping', 'course_name') 
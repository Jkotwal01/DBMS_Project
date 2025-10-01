"""Initial schema

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema"""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('Student', 'Faculty', 'Admin', 'Parent', 'Management', name='roleenum'), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('user_id'),
        sa.UniqueConstraint('email')
    )
    op.create_index('ix_users_user_id', 'users', ['user_id'])
    op.create_index('ix_users_email', 'users', ['email'])
    op.create_index('ix_users_role', 'users', ['role'])
    
    # Students table
    op.create_table(
        'students',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('roll_no', sa.String(length=50), nullable=False),
        sa.Column('class_name', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('section', sa.String(length=10), nullable=True),
        sa.Column('division', sa.String(length=10), nullable=True),
        sa.Column('batch', sa.String(length=50), nullable=True),
        sa.Column('admission_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['student_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('student_id'),
        sa.UniqueConstraint('roll_no')
    )
    op.create_index('ix_students_roll_no', 'students', ['roll_no'])
    
    # Faculty table
    op.create_table(
        'faculty',
        sa.Column('faculty_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=True),
        sa.Column('designation', sa.String(length=50), nullable=True),
        sa.Column('dept', sa.String(length=100), nullable=True),
        sa.Column('specialization', sa.String(length=100), nullable=True),
        sa.Column('joining_date', sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(['faculty_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('faculty_id'),
        sa.UniqueConstraint('employee_id')
    )
    
    # Subjects table
    op.create_table(
        'subjects',
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('subject_code', sa.String(length=20), nullable=True),
        sa.Column('subject_name', sa.String(length=100), nullable=False),
        sa.Column('faculty_id', sa.Integer(), nullable=True),
        sa.Column('semester', sa.Integer(), nullable=True),
        sa.Column('credits', sa.Integer(), default=3),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['faculty_id'], ['faculty.faculty_id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('subject_id'),
        sa.UniqueConstraint('subject_code')
    )
    op.create_index('ix_subjects_subject_id', 'subjects', ['subject_id'])
    
    # Timetable table
    op.create_table(
        'timetable',
        sa.Column('timetable_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('day', sa.String(length=10), nullable=True),
        sa.Column('time_slot', sa.String(length=30), nullable=True),
        sa.Column('room_number', sa.String(length=20), nullable=True),
        sa.Column('semester', sa.Integer(), nullable=True),
        sa.Column('academic_year', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.subject_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('timetable_id'),
        sa.UniqueConstraint('student_id', 'day', 'time_slot', name='u_student_day_time')
    )
    op.create_index('ix_timetable_timetable_id', 'timetable', ['timetable_id'])
    
    # Attendance table
    op.create_table(
        'attendance',
        sa.Column('attendance_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('date', sa.Date(), nullable=True),
        sa.Column('status', sa.String(length=10), nullable=True),
        sa.Column('marked_by', sa.Integer(), nullable=True),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['marked_by'], ['faculty.faculty_id'], ondelete='SET NULL'),
        sa.ForeignKeyConstraint(['student_id'], ['students.student_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['subject_id'], ['subjects.subject_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('attendance_id'),
        sa.UniqueConstraint('student_id', 'subject_id', 'date', name='u_student_subject_date')
    )
    op.create_index('ix_attendance_attendance_id', 'attendance', ['attendance_id'])
    op.create_index('ix_attendance_date', 'attendance', ['date'])
    
    # Notifications table
    op.create_table(
        'notifications',
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=False),
        sa.Column('visible_to', sa.String(length=20), default='Student'),
        sa.Column('priority', sa.String(length=10), default='normal'),
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP')),
        sa.ForeignKeyConstraint(['created_by'], ['faculty.faculty_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('notification_id')
    )
    op.create_index('ix_notifications_notification_id', 'notifications', ['notification_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_table('notifications')
    op.drop_table('attendance')
    op.drop_table('timetable')
    op.drop_table('subjects')
    op.drop_table('faculty')
    op.drop_table('students')
    op.drop_table('users')

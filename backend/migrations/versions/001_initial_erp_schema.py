"""Initial ERP schema migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create users table
    op.create_table('users',
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('role', sa.Enum('STUDENT', 'FACULTY', 'ADMIN', 'PARENT', 'MANAGEMENT', name='roleenum'), nullable=False),
        sa.Column('department', sa.String(length=100), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('date_of_birth', sa.Date(), nullable=True),
        sa.Column('gender', sa.String(length=10), nullable=True),
        sa.Column('status', sa.Enum('ACTIVE', 'INACTIVE', 'SUSPENDED', 'GRADUATED', name='statusenum'), nullable=True),
        sa.Column('profile_picture', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('last_login', sa.TIMESTAMP(), nullable=True),
        sa.PrimaryKeyConstraint('user_id')
    )
    op.create_index(op.f('ix_users_user_id'), 'users', ['user_id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)

    # Create departments table
    op.create_table('departments',
        sa.Column('dept_id', sa.Integer(), nullable=False),
        sa.Column('dept_name', sa.String(length=100), nullable=False),
        sa.Column('dept_code', sa.String(length=10), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('head_faculty_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('dept_id'),
        sa.UniqueConstraint('dept_code'),
        sa.UniqueConstraint('dept_name')
    )
    op.create_index(op.f('ix_departments_dept_id'), 'departments', ['dept_id'], unique=False)

    # Create academic_years table
    op.create_table('academic_years',
        sa.Column('year_id', sa.Integer(), nullable=False),
        sa.Column('year_name', sa.String(length=50), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('year_id'),
        sa.UniqueConstraint('year_name')
    )
    op.create_index(op.f('ix_academic_years_year_id'), 'academic_years', ['year_id'], unique=False)

    # Create semesters table
    op.create_table('semesters',
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('semester_name', sa.String(length=50), nullable=False),
        sa.Column('academic_year_id', sa.Integer(), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=False),
        sa.Column('is_current', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('semester_id')
    )
    op.create_index(op.f('ix_semesters_semester_id'), 'semesters', ['semester_id'], unique=False)
    op.create_foreign_key(None, 'semesters', 'academic_years', ['academic_year_id'], ['year_id'], ondelete='CASCADE')

    # Create students table
    op.create_table('students',
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('roll_no', sa.String(length=50), nullable=False),
        sa.Column('student_id_number', sa.String(length=50), nullable=True),
        sa.Column('class_name', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('section', sa.String(length=10), nullable=True),
        sa.Column('batch', sa.String(length=20), nullable=True),
        sa.Column('dept_id', sa.Integer(), nullable=True),
        sa.Column('current_semester_id', sa.Integer(), nullable=True),
        sa.Column('enrollment_date', sa.Date(), nullable=True),
        sa.Column('gpa', sa.Float(), nullable=True),
        sa.Column('total_credits', sa.Integer(), nullable=True),
        sa.Column('emergency_contact', sa.String(length=100), nullable=True),
        sa.Column('emergency_phone', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('student_id'),
        sa.UniqueConstraint('roll_no'),
        sa.UniqueConstraint('student_id_number')
    )
    op.create_foreign_key(None, 'students', 'users', ['student_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'students', 'departments', ['dept_id'], ['dept_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'students', 'semesters', ['current_semester_id'], ['semester_id'], ondelete='SET NULL')

    # Create faculty table
    op.create_table('faculty',
        sa.Column('faculty_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=50), nullable=True),
        sa.Column('dept_id', sa.Integer(), nullable=True),
        sa.Column('qualification', sa.Text(), nullable=True),
        sa.Column('specialization', sa.Text(), nullable=True),
        sa.Column('experience_years', sa.Integer(), nullable=True),
        sa.Column('joining_date', sa.Date(), nullable=True),
        sa.Column('salary', sa.Float(), nullable=True),
        sa.Column('is_head', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('faculty_id'),
        sa.UniqueConstraint('employee_id')
    )
    op.create_foreign_key(None, 'faculty', 'users', ['faculty_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'faculty', 'departments', ['dept_id'], ['dept_id'], ondelete='SET NULL')

    # Create admins table
    op.create_table('admins',
        sa.Column('admin_id', sa.Integer(), nullable=False),
        sa.Column('employee_id', sa.String(length=50), nullable=False),
        sa.Column('designation', sa.String(length=50), nullable=True),
        sa.Column('dept_id', sa.Integer(), nullable=True),
        sa.Column('permissions', sa.JSON(), nullable=True),
        sa.Column('joining_date', sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint('admin_id'),
        sa.UniqueConstraint('employee_id')
    )
    op.create_foreign_key(None, 'admins', 'users', ['admin_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'admins', 'departments', ['dept_id'], ['dept_id'], ondelete='SET NULL')

    # Create parents table
    op.create_table('parents',
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('occupation', sa.String(length=100), nullable=True),
        sa.Column('workplace', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('parent_id')
    )
    op.create_foreign_key(None, 'parents', 'users', ['parent_id'], ['user_id'], ondelete='CASCADE')

    # Create parent_students table
    op.create_table('parent_students',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('relationship_type', sa.String(length=20), nullable=False),
        sa.Column('is_primary', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_parent_students_id'), 'parent_students', ['id'], unique=False)
    op.create_foreign_key(None, 'parent_students', 'parents', ['parent_id'], ['parent_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'parent_students', 'students', ['student_id'], ['student_id'], ondelete='CASCADE')

    # Create subjects table
    op.create_table('subjects',
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('subject_code', sa.String(length=20), nullable=False),
        sa.Column('subject_name', sa.String(length=100), nullable=False),
        sa.Column('faculty_id', sa.Integer(), nullable=True),
        sa.Column('dept_id', sa.Integer(), nullable=True),
        sa.Column('credits', sa.Integer(), nullable=True),
        sa.Column('semester', sa.Integer(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('is_elective', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('subject_id'),
        sa.UniqueConstraint('subject_code')
    )
    op.create_index(op.f('ix_subjects_subject_id'), 'subjects', ['subject_id'], unique=False)
    op.create_foreign_key(None, 'subjects', 'faculty', ['faculty_id'], ['faculty_id'], ondelete='SET NULL')
    op.create_foreign_key(None, 'subjects', 'departments', ['dept_id'], ['dept_id'], ondelete='SET NULL')

    # Create enrollments table
    op.create_table('enrollments',
        sa.Column('enrollment_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('enrollment_date', sa.Date(), nullable=False),
        sa.Column('grade', sa.String(length=5), nullable=True),
        sa.Column('credits_earned', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=True),
        sa.PrimaryKeyConstraint('enrollment_id')
    )
    op.create_index(op.f('ix_enrollments_enrollment_id'), 'enrollments', ['enrollment_id'], unique=False)
    op.create_foreign_key(None, 'enrollments', 'students', ['student_id'], ['student_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'enrollments', 'subjects', ['subject_id'], ['subject_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'enrollments', 'semesters', ['semester_id'], ['semester_id'], ondelete='CASCADE')

    # Create timetable table
    op.create_table('timetable',
        sa.Column('timetable_id', sa.Integer(), nullable=False),
        sa.Column('subject_id', sa.Integer(), nullable=False),
        sa.Column('faculty_id', sa.Integer(), nullable=False),
        sa.Column('class_room', sa.String(length=50), nullable=True),
        sa.Column('day', sa.String(length=10), nullable=False),
        sa.Column('start_time', sa.String(length=10), nullable=False),
        sa.Column('end_time', sa.String(length=10), nullable=False),
        sa.Column('semester_id', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('timetable_id')
    )
    op.create_index(op.f('ix_timetable_timetable_id'), 'timetable', ['timetable_id'], unique=False)
    op.create_foreign_key(None, 'timetable', 'subjects', ['subject_id'], ['subject_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'timetable', 'faculty', ['faculty_id'], ['faculty_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'timetable', 'semesters', ['semester_id'], ['semester_id'], ondelete='CASCADE')

    # Create attendance_sessions table
    op.create_table('attendance_sessions',
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('timetable_id', sa.Integer(), nullable=False),
        sa.Column('session_date', sa.Date(), nullable=False),
        sa.Column('start_time', sa.String(length=10), nullable=True),
        sa.Column('end_time', sa.String(length=10), nullable=True),
        sa.Column('is_completed', sa.Boolean(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('session_id')
    )
    op.create_index(op.f('ix_attendance_sessions_session_id'), 'attendance_sessions', ['session_id'], unique=False)
    op.create_foreign_key(None, 'attendance_sessions', 'timetable', ['timetable_id'], ['timetable_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'attendance_sessions', 'faculty', ['created_by'], ['faculty_id'], ondelete='SET NULL')

    # Create attendance table
    op.create_table('attendance',
        sa.Column('attendance_id', sa.Integer(), nullable=False),
        sa.Column('session_id', sa.Integer(), nullable=False),
        sa.Column('student_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('PRESENT', 'ABSENT', 'LATE', 'EXCUSED', name='attendancestatusenum'), nullable=False),
        sa.Column('remarks', sa.Text(), nullable=True),
        sa.Column('marked_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('marked_by', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('attendance_id')
    )
    op.create_index(op.f('ix_attendance_attendance_id'), 'attendance', ['attendance_id'], unique=False)
    op.create_foreign_key(None, 'attendance', 'attendance_sessions', ['session_id'], ['session_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'attendance', 'students', ['student_id'], ['student_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'attendance', 'faculty', ['marked_by'], ['faculty_id'], ondelete='SET NULL')

    # Create notifications table
    op.create_table('notifications',
        sa.Column('notification_id', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('message', sa.LONGTEXT(), nullable=False),
        sa.Column('notification_type', sa.Enum('GENERAL', 'ATTENDANCE', 'ACADEMIC', 'ADMINISTRATIVE', 'EMERGENCY', name='notificationtypeenum'), nullable=True),
        sa.Column('sender_id', sa.Integer(), nullable=True),
        sa.Column('receiver_id', sa.Integer(), nullable=True),
        sa.Column('created_by', sa.Integer(), nullable=True),
        sa.Column('target_role', sa.Enum('STUDENT', 'FACULTY', 'ADMIN', 'PARENT', 'MANAGEMENT', name='roleenum'), nullable=True),
        sa.Column('target_department', sa.Integer(), nullable=True),
        sa.Column('is_broadcast', sa.Boolean(), nullable=True),
        sa.Column('is_urgent', sa.Boolean(), nullable=True),
        sa.Column('scheduled_for', sa.TIMESTAMP(), nullable=True),
        sa.Column('expires_at', sa.TIMESTAMP(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('notification_id')
    )
    op.create_index(op.f('ix_notifications_notification_id'), 'notifications', ['notification_id'], unique=False)
    op.create_foreign_key(None, 'notifications', 'users', ['sender_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'notifications', 'users', ['receiver_id'], ['user_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'notifications', 'faculty', ['created_by'], ['faculty_id'], ondelete='CASCADE')
    op.create_foreign_key(None, 'notifications', 'departments', ['target_department'], ['dept_id'], ondelete='SET NULL')

    # Create login_logs table
    op.create_table('login_logs',
        sa.Column('log_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('user_agent', sa.Text(), nullable=True),
        sa.Column('login_time', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.Column('logout_time', sa.TIMESTAMP(), nullable=True),
        sa.Column('is_successful', sa.Boolean(), nullable=False),
        sa.Column('failure_reason', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('log_id')
    )
    op.create_index(op.f('ix_login_logs_log_id'), 'login_logs', ['log_id'], unique=False)
    op.create_foreign_key(None, 'login_logs', 'users', ['user_id'], ['user_id'], ondelete='CASCADE')

    # Create audit_logs table
    op.create_table('audit_logs',
        sa.Column('audit_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('action', sa.String(length=100), nullable=False),
        sa.Column('table_name', sa.String(length=50), nullable=False),
        sa.Column('record_id', sa.Integer(), nullable=True),
        sa.Column('old_values', sa.JSON(), nullable=True),
        sa.Column('new_values', sa.JSON(), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('timestamp', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('audit_id')
    )
    op.create_index(op.f('ix_audit_logs_audit_id'), 'audit_logs', ['audit_id'], unique=False)
    op.create_foreign_key(None, 'audit_logs', 'users', ['user_id'], ['user_id'], ondelete='SET NULL')

    # Create file_uploads table
    op.create_table('file_uploads',
        sa.Column('file_id', sa.Integer(), nullable=False),
        sa.Column('filename', sa.String(length=255), nullable=False),
        sa.Column('original_filename', sa.String(length=255), nullable=False),
        sa.Column('file_path', sa.String(length=500), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(length=100), nullable=False),
        sa.Column('uploaded_by', sa.Integer(), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=True),
        sa.Column('is_processed', sa.Boolean(), nullable=True),
        sa.Column('upload_date', sa.TIMESTAMP(), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('file_id')
    )
    op.create_index(op.f('ix_file_uploads_file_id'), 'file_uploads', ['file_id'], unique=False)
    op.create_foreign_key(None, 'file_uploads', 'users', ['uploaded_by'], ['user_id'], ondelete='CASCADE')

    # Add foreign key constraints for departments head_faculty_id
    op.create_foreign_key(None, 'departments', 'faculty', ['head_faculty_id'], ['faculty_id'], ondelete='SET NULL')


def downgrade():
    # Drop all tables in reverse order
    op.drop_table('file_uploads')
    op.drop_table('audit_logs')
    op.drop_table('login_logs')
    op.drop_table('notifications')
    op.drop_table('attendance')
    op.drop_table('attendance_sessions')
    op.drop_table('timetable')
    op.drop_table('enrollments')
    op.drop_table('subjects')
    op.drop_table('parent_students')
    op.drop_table('parents')
    op.drop_table('admins')
    op.drop_table('faculty')
    op.drop_table('students')
    op.drop_table('semesters')
    op.drop_table('academic_years')
    op.drop_table('departments')
    op.drop_table('users')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS roleenum')
    op.execute('DROP TYPE IF EXISTS statusenum')
    op.execute('DROP TYPE IF EXISTS attendancestatusenum')
    op.execute('DROP TYPE IF EXISTS notificationtypeenum')
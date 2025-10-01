# utils/csv_processor.py
import csv
import io
from typing import List, Dict
from fastapi import UploadFile

class CSVProcessor:
    """Utility class for processing CSV files"""
    
    @staticmethod
    async def parse_student_csv(file: UploadFile) -> List[Dict]:
        """
        Parse CSV file containing student data.
        Expected columns: name, email, roll_no, class_name, year, section, division, department, phone
        """
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        students = []
        for row in csv_reader:
            student_data = {
                'name': row.get('name', '').strip(),
                'email': row.get('email', '').strip(),
                'password': row.get('password', 'student123').strip(),
                'roll_no': row.get('roll_no', '').strip(),
                'class_name': row.get('class_name', '').strip(),
                'year': int(row.get('year', 0)) if row.get('year', '').strip() else None,
                'section': row.get('section', '').strip(),
                'division': row.get('division', '').strip(),
                'batch': row.get('batch', '').strip(),
                'department': row.get('department', '').strip(),
                'phone': row.get('phone', '').strip(),
                'address': row.get('address', '').strip()
            }
            
            # Only add if required fields are present
            if student_data['name'] and student_data['email'] and student_data['roll_no']:
                students.append(student_data)
        
        return students
    
    @staticmethod
    async def parse_attendance_csv(file: UploadFile) -> List[Dict]:
        """
        Parse CSV file containing attendance data.
        Expected columns: student_id or roll_no, status, remarks
        """
        contents = await file.read()
        decoded = contents.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(decoded))
        
        attendance_records = []
        for row in csv_reader:
            record = {
                'student_id': int(row.get('student_id', 0)) if row.get('student_id', '').strip() else None,
                'roll_no': row.get('roll_no', '').strip(),
                'status': row.get('status', 'Present').strip(),
                'remarks': row.get('remarks', '').strip()
            }
            
            if record['student_id'] or record['roll_no']:
                attendance_records.append(record)
        
        return attendance_records
    
    @staticmethod
    def generate_sample_student_csv() -> str:
        """Generate a sample CSV template for student upload"""
        output = io.StringIO()
        fieldnames = ['name', 'email', 'password', 'roll_no', 'class_name', 'year', 'section', 'division', 'batch', 'department', 'phone', 'address']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        
        writer.writeheader()
        writer.writerow({
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'password': 'student123',
            'roll_no': 'CS2024001',
            'class_name': 'Computer Science',
            'year': '2',
            'section': 'A',
            'division': '1',
            'batch': '2024',
            'department': 'Computer Science',
            'phone': '1234567890',
            'address': '123 Main St'
        })
        
        return output.getvalue()
    
    @staticmethod
    def validate_student_data(student_data: Dict) -> tuple[bool, str]:
        """Validate student data"""
        required_fields = ['name', 'email', 'roll_no']
        
        for field in required_fields:
            if not student_data.get(field):
                return False, f"Missing required field: {field}"
        
        # Email validation (basic)
        if '@' not in student_data['email']:
            return False, "Invalid email format"
        
        return True, "Valid"

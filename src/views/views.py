"""
View layer for displaying information to users (MVC Pattern)
"""
from typing import Dict, Any, List
from datetime import datetime
from src.models.models import Student, AttendanceRecord


class ConsoleView:
    """Console-based view for displaying information"""

    @staticmethod
    def display_menu():
        """Display main menu"""
        print("\n" + "="*60)
        print("  FACE RECOGNITION ATTENDANCE SYSTEM")
        print("="*60)
        print("\n[STUDENT MANAGEMENT]")
        print("1. Register new student")
        print("2. Add face image to student")
        print("3. View student information")
        print("4. List all students")
        print("5. Update student information")
        print("6. Delete student")

        print("\n[ATTENDANCE]")
        print("7. Take attendance from image")
        print("8. Take attendance from webcam")
        print("9. View today's attendance")
        print("10. View attendance by date")
        print("11. View student attendance history")
        print("12. Generate attendance report")

        print("\n[SETTINGS]")
        print("13. Change recognition model")
        print("14. View available models")

        print("\n[OTHER]")
        print("15. Test face recognition")
        print("0. Exit")
        print("="*60)

    @staticmethod
    def display_success(message: str):
        """Display success message"""
        print(f"\n✓ SUCCESS: {message}")

    @staticmethod
    def display_error(message: str):
        """Display error message"""
        print(f"\n✗ ERROR: {message}")

    @staticmethod
    def display_info(message: str):
        """Display information message"""
        print(f"\nℹ INFO: {message}")

    @staticmethod
    def display_warning(message: str):
        """Display warning message"""
        print(f"\n⚠ WARNING: {message}")

    @staticmethod
    def display_student(student: Student):
        """Display student information"""
        print("\n" + "-"*60)
        print("STUDENT INFORMATION")
        print("-"*60)
        print(f"Student ID:   {student.student_id}")
        print(f"Full Name:    {student.full_name}")
        print(f"Class:        {student.class_name}")
        print(f"Email:        {student.email or 'N/A'}")
        print(f"Face Image:   {'Registered' if student.face_encoding_path else 'Not registered'}")
        print(f"Created:      {student.created_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print("-"*60)

    @staticmethod
    def display_students_list(students: List[Student]):
        """Display list of students"""
        if not students:
            print("\nNo students found.")
            return

        print("\n" + "="*100)
        print(f"{'ID':<15} {'Name':<25} {'Class':<15} {'Email':<25} {'Face':<10}")
        print("="*100)

        for student in students:
            face_status = "✓" if student.face_encoding_path else "✗"
            email = student.email[:22] + "..." if student.email and len(student.email) > 25 else (student.email or "N/A")
            print(f"{student.student_id:<15} {student.full_name:<25} {student.class_name:<15} {email:<25} {face_status:<10}")

        print("="*100)
        print(f"Total: {len(students)} student(s)")

    @staticmethod
    def display_attendance_record(record: AttendanceRecord):
        """Display single attendance record"""
        print("\n" + "-"*60)
        print("ATTENDANCE RECORD")
        print("-"*60)
        print(f"Student ID:   {record.student_id}")
        print(f"Date:         {record.session_date}")
        print(f"Check-in:     {record.check_in_time.strftime('%H:%M:%S')}")
        print(f"Status:       {record.status.upper()}")
        print(f"Confidence:   {record.confidence:.2%}" if record.confidence else "Confidence:   N/A")
        print(f"Model:        {record.model_used}")
        print(f"Notes:        {record.notes or 'N/A'}")
        print("-"*60)

    @staticmethod
    def display_attendance_list(records: List[AttendanceRecord], date: str = None):
        """Display list of attendance records"""
        if not records:
            print("\nNo attendance records found.")
            return

        title = f"ATTENDANCE RECORDS - {date}" if date else "ATTENDANCE RECORDS"
        print("\n" + "="*100)
        print(title)
        print("="*100)
        print(f"{'Student ID':<15} {'Check-in Time':<20} {'Status':<12} {'Confidence':<12} {'Model':<20}")
        print("="*100)

        for record in records:
            check_in = record.check_in_time.strftime('%Y-%m-%d %H:%M:%S')
            confidence = f"{record.confidence:.2%}" if record.confidence else "N/A"
            print(f"{record.student_id:<15} {check_in:<20} {record.status:<12} {confidence:<12} {record.model_used:<20}")

        print("="*100)
        print(f"Total: {len(records)} record(s)")

    @staticmethod
    def display_attendance_report(report: Dict[str, Any]):
        """Display attendance report"""
        print("\n" + "="*60)
        print(f"ATTENDANCE REPORT - {report['date']}")
        print("="*60)
        print(f"Total Records:  {report['total_records']}")
        print(f"Present:        {report['present']} ({report['present']/report['total_records']*100:.1f}%)" if report['total_records'] > 0 else "Present:        0")
        print(f"Late:           {report['late']}")
        print(f"Absent:         {report['absent']}")
        print("="*60)

    @staticmethod
    def display_recognition_result(result: Dict[str, Any]):
        """Display face recognition result"""
        print("\n" + "-"*60)
        print("FACE RECOGNITION RESULT")
        print("-"*60)

        if result.get('recognized', False):
            rec_result = result['result']
            print(f"✓ RECOGNIZED")
            print(f"Student ID:   {rec_result.student_id}")
            print(f"Name:         {rec_result.student_name}")
            print(f"Confidence:   {rec_result.confidence:.2%}")
            print(f"Distance:     {rec_result.distance:.4f}")
            print(f"Model Used:   {rec_result.model_used}")
        else:
            print(f"✗ NOT RECOGNIZED")
            if 'result' in result:
                rec_result = result['result']
                print(f"Model Used:   {rec_result.model_used}")

        print("-"*60)

    @staticmethod
    def display_models_list(models: List[str], current: str = None):
        """Display available models"""
        print("\n" + "="*60)
        print("AVAILABLE FACE RECOGNITION MODELS")
        print("="*60)
        for i, model in enumerate(models, 1):
            marker = " (current)" if model == current else ""
            print(f"{i}. {model}{marker}")
        print("="*60)

    @staticmethod
    def get_input(prompt: str) -> str:
        """Get user input"""
        return input(f"\n{prompt}: ").strip()

    @staticmethod
    def get_choice() -> str:
        """Get menu choice"""
        return input("\nEnter your choice: ").strip()

    @staticmethod
    def pause():
        """Pause and wait for user"""
        input("\nPress Enter to continue...")

    @staticmethod
    def clear_screen():
        """Clear console screen"""
        import os
        os.system('clear' if os.name == 'posix' else 'cls')


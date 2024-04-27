from enum import Enum

class NavbarMenu(Enum):

    TEACHER= "TEACHER"
    STUDENTS= "STUDENTS"
    ORGANIZATION= "ORGANIZATION"

class AccountDetails(Enum):

    STUDENT_FIRST_NAME = "Student2"
    STUDENT_LAST_NAME = "test"
    CONTACT = "1234567890"
    ADDRESS = "Old City"
    STUDENT_USERNAME= "student2"
    STUDENT_PASSWORD= "student2"
    EMAIL = "student@gmail.com"
    ORGANIZATION = "Techno"
    NEW_FIRST_NAME = "Student-Latest"

class LoginDetails(Enum):

    STUDENT_USERNAME="Student1"
    STUDENT_PASSWORD="Student1"

    TEACHER_USERNAME="Teacher1"
    TEACHER_PASSWORD="Teacher1"

class CourseDetails(Enum):
    COURSE_NAME = "Test course 1"
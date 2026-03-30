from flask import Flask, request
from flask_cors import CORS
from dbSetup import db, Course, User, Enrollment

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///enrollment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

print("APP DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
print("APP instance path:", app.instance_path)

db.init_app(app)

with app.app_context():
    db.create_all()


@app.route("/")
def home():
    return {"message": "Backend running"}

@app.route("/api/courses")
def get_courses():
    courses = Course.query.all()

    course_list = []

    for course in courses:
        course_data = {
            "id": course.id,
            "course_name": course.course_name,
            "schedule": course.schedule,
            "capacity": course.capacity,
            "enrolled_count": course.enrolled_count,
            "teacher_name": course.teacher.name
        }
        course_list.append(course_data)

    return course_list

@app.route("/api/student/<int:student_id>/courses")
def get_student_courses(student_id):
    student = User.query.get(student_id)

    result = []
    for enrollment in student.enrollments:
        result.append({
            "course_id": enrollment.course.id,
            "course_name": enrollment.course.course_name,
            "schedule": enrollment.course.schedule,
            "grade": enrollment.grade
        })

    return result

@app.route("/api/student/<int:student_id>/enroll/<int:course_id>", methods=["POST"])
def enroll_student(student_id, course_id):
    student = User.query.get(student_id)
    course = Course.query.get(course_id)

    if not student:
        return {"error": "Student not found"}, 404
    
    if not course:
        return {"error": "Course not found"}, 404
    
    existing_enrollment = Enrollment.query.filter_by(
        student_id=student_id,
        course_id=course_id
    ).first()

    if existing_enrollment:
        return {"error": "Student already enrolled"}, 400
    
    if course.is_full:
        return {"error": "Course is full"}, 400
    
    new_enrollment = Enrollment(
        student_id=student_id,
        course_id=course_id
    )

    db.session.add(new_enrollment)
    db.session.commit()

    return {
        "message": "Enrollment successful",
        "student": student.name,
        "course": course.course_name
    }

@app.route("/api/teacher/<int:teacher_id>/courses")
def get_teacher_courses(teacher_id):
    teacher = User.query.get(teacher_id)

    if not teacher:
        return {"error": "Teacher not found"}, 404
    
    courses = teacher.courses_taught

    result = []
    for course in courses:
        result.append({
            "id": course.id,
            "course_name": course.course_name,
            "schedule": course.schedule,
            "capacity": course.capacity,
            "enrolled_count": course.enrolled_count
        })

    return result

@app.route("/api/teacher/course/<int:course_id>/students")
def get_course_students(course_id):
    course = Course.query.get(course_id)

    if not course:
        return {"error": "Course not found"}, 404

    enrollments = course.enrollments

    result = []

    for enrollment in enrollments:
        result.append({
            "student_id": enrollment.student.id,
            "student_name": enrollment.student.name,
            "grade": enrollment.grade,
            "enrollment_id": enrollment.id
        })
    
    return result

@app.route("/api/teacher/enrollment/<int:enrollment_id>/grade", methods=["PUT"])
def update_grade(enrollment_id):    
    enrollment = Enrollment.query.get(enrollment_id)

    if not enrollment:
        return {"error": "Enrollment not found"}, 404
    
    data = request.get_json()
    new_grade = data.get("grade")

    enrollment.grade = new_grade
    db.session.commit()
    
    return {
        "message": "Grade updated",
        "student": enrollment.student.name,
        "course": enrollment.course.course_name,
        "new_grade": new_grade
    }

# Login
@app.route("/api/login", methods=["POST"])
def login():
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    user = User.query.filter_by(username=username, password=password).first()

    if not user:
        return {"error": "Invalid username or password"}, 401

    return {
        "id": user.id,
        "name": user.name,
        "role": user.role,
        "username": user.username
    }


if __name__ == "__main__":
    app.run(debug=True)
from flask import Flask, request
from flask_cors import CORS
from dbSetup import db, Course, User, Enrollment
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from sqlalchemy.pool import NullPool
from flask_admin.form.fields import Select2Field
from flask_admin.form.validators import FieldListInputRequired
from flask_admin.contrib.sqla.fields import QuerySelectField, QuerySelectMultipleField
from flask_admin.contrib.sqla.validators import Unique


def patch_flask_admin_for_wtforms3():
    FieldListInputRequired.field_flags = {"required": True}
    Unique.field_flags = {"unique": True}

    def iter_select2_choices(self):
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None, {})

        for choice in self.choices:
            if isinstance(choice, tuple):
                yield (choice[0], choice[1], self.coerce(choice[0]) == self.data, {})
            else:
                yield (choice.value, choice.name, self.coerce(choice.value) == self.data, {})

    def iter_query_choices(self):
        if self.allow_blank:
            yield ("__None", self.blank_text, self.data is None, {})

        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj == self.data, {})

    def iter_query_multiple_choices(self):
        selected = self.data or []

        for pk, obj in self._get_object_list():
            yield (pk, self.get_label(obj), obj in selected, {})

    Select2Field.iter_choices = iter_select2_choices
    QuerySelectField.iter_choices = iter_query_choices
    QuerySelectMultipleField.iter_choices = iter_query_multiple_choices


patch_flask_admin_for_wtforms3()

app = Flask(__name__)
app.secret_key = "secretkeything"
CORS(app)

admin = Admin(app, name="Admin")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///enrollment.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "poolclass": NullPool
}

print("APP DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
print("APP instance path:", app.instance_path)

db.init_app(app)

class UserAdmin(ModelView):
    column_list = ["id", "name", "username", "password", "role", "email"]
    form_columns = ["name", "username", "password", "role", "email"]


class CourseAdmin(ModelView):
    column_list = ["id", "course_name", "schedule", "capacity", "teacher"]
    form_columns = ["course_name", "schedule", "capacity", "teacher"]


class EnrollmentAdmin(ModelView):
    column_list = ["id", "student", "course", "grade"]
    form_columns = ["student", "course", "grade"]

class SecureModelView(ModelView):
    def is_accessible(self):
        return True

admin.add_view(UserAdmin(User, db.session))
admin.add_view(CourseAdmin(Course, db.session))
admin.add_view(EnrollmentAdmin(Enrollment, db.session))

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

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import CheckConstraint, UniqueConstraint

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    username = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)

    __table_args__ = (
        CheckConstraint(
            "role IN ('student', 'teacher', 'admin')",
            name="check_valid_role"
        ),
    )

    courses_taught = db.relationship(
        "Course",
        back_populates="teacher",
        foreign_keys="Course.teacher_id",
        cascade="all, delete-orphan"
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="student",
        foreign_keys="Enrollment.student_id",
        cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<User id={self.id} username={self.username} role={self.role}>"


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)
    course_name = db.Column(db.String(100), nullable=False)
    schedule = db.Column(db.String(100), nullable=False)
    capacity = db.Column(db.Integer, nullable=False)

    teacher_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    teacher = db.relationship(
        "User",
        back_populates="courses_taught",
        foreign_keys=[teacher_id]
    )

    enrollments = db.relationship(
        "Enrollment",
        back_populates="course",
        cascade="all, delete-orphan"
    )

    @property
    def enrolled_count(self):
        return len(self.enrollments)

    @property
    def is_full(self):
        return self.enrolled_count >= self.capacity

    def __repr__(self):
        return f"<Course id={self.id} name={self.course_name}>"


class Enrollment(db.Model):
    __tablename__ = "enrollments"

    id = db.Column(db.Integer, primary_key=True)

    student_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    grade = db.Column(db.Integer, nullable=True)

    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="unique_student_course"),
    )

    student = db.relationship(
        "User",
        back_populates="enrollments",
        foreign_keys=[student_id]
    )

    course = db.relationship(
        "Course",
        back_populates="enrollments"
    )

    def __repr__(self):
        return f"<Enrollment student_id={self.student_id} course_id={self.course_id}>"
from app import app
from dbSetup import db, User, Course, Enrollment

print("TEST DB URI:", app.config["SQLALCHEMY_DATABASE_URI"])
print("TEST instance path:", app.instance_path)

with app.app_context():
    db.drop_all()
    db.create_all()

    teacher = User(
        name="Jake W",
        role="teacher",
        username="jake123",
        password="1234",
        email="jkw@zzz.com"
    )

    student = User(
        name="Jillian",
        role="student",
        username="jilxio",
        password="1234",
        email="jxio@zzz.com"
    )

    db.session.add_all([teacher, student])
    db.session.commit()

    course = Course(
        course_name="CSE 100",
        schedule="MWF 2:00-2:50 PM",
        capacity=10,
        teacher_id=teacher.id
    )

    db.session.add(course)
    db.session.commit()

    enrollment = Enrollment(
        student_id=student.id,
        course_id=course.id,
        grade=95
    )

    db.session.add(enrollment)
    db.session.commit()

    newCourse = Course(
        course_name="CSE 120",
        schedule="MWF 2:00-2:50 PM",
        capacity = 0,
        teacher_id=teacher.id
    )
    db.session.add(newCourse)
    db.session.commit()

    print("Data inputted")
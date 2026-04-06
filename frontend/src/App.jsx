import { useState, useEffect } from "react"

function App() {
  const [courses, setCourses] = useState([])
  const [message, setMessage] = useState("")
  const [studentCourses, setStudentCourses] = useState([])
  const [teacherCourses, setTeacherCourses] = useState([])
  const [courseStudents, setCourseStudents] = useState([])
  const [selectedCourseId, setSelectedCourseId] = useState(null)

  const [roleView, setRoleView] = useState("student")

  const [user, setUser] = useState(null)
  const [username, setUsername]  = useState("")
  const [password, setPassword] = useState("")

  const loadCourses = () => {
    fetch(`http://127.0.0.1:5000/api/courses`)
      .then(res => res.json())
      .then(data => setCourses(data))
  }

  const loadStudentCourses = () => {
    fetch(`http://127.0.0.1:5000/api/student/${user.id}/courses`)
      .then(response => response.json())
      .then(data => setStudentCourses(data))
      .catch(error => console.error("Error:", error))
  }

  const loadTeacherCourses = () => {
    fetch(`http://127.0.0.1:5000/api/teacher/${user.id}/courses`)
      .then(response => response.json())
      .then(data => setTeacherCourses(data))
      .catch(error => console.error("Error:", error))
  }

  const loadCourseStudents = (courseId) => {
    setSelectedCourseId(courseId)
    fetch(`http://127.0.0.1:5000/api/teacher/course/${courseId}/students`)
      .then(response => response.json())
      .then(data => setCourseStudents(data))
      .catch(error => console.error("Error:", error))
  }

  const updateGrade = (enrollmentId, studentId) => {
    const input = document.getElementById(`grade-${studentId}`)
    const newGrade = input.value

    fetch(`http://127.0.0.1:5000/api/teacher/enrollment/${enrollmentId}/grade`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ grade: newGrade })
    })
      .then(response => response.json())
      .then(data => {
        if (data.message) {
          setMessage(data.message)
          loadCourseStudents(selectedCourseId)
        } else if (data.error) {
          setMessage(data.error)
        }
      })
  }

  const isAlreadyEnrolled = (courseId) => {
    return studentCourses.some((course) => course.course_id === courseId)
  }

  const handleLogin = () => {
    fetch(`http://127.0.0.1:5000/api/login`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    })
      .then(response => response.json())
      .then(data => {
        if (data.error){
          setMessage(data.error)
        } else {
          setUser(data)
          setRoleView(data.role)
          setMessage(`Welcome back ${data.name}`)
        }
      })
      .catch(err => console.error(err))
  }


  useEffect(() => {
    if (user) {
      loadCourses()

      if (user.role === "student") {
        loadStudentCourses()
      }

      if (user.role === "teacher") {
        loadTeacherCourses()
      }
    }
  }, [user])

  const handleEnroll = (courseId) => {
    fetch(`http://127.0.0.1:5000/api/student/${user.id}/enroll/${courseId}`, {
      method: "POST"
    })
      .then(response => response.json())
      .then(data => {
        if (data.message){
          setMessage(data.message)
          loadCourses()
          loadStudentCourses()
          loadTeacherCourses()
        } else if (data.error){
          setMessage(data.error)
        }
      })
      .catch(error => console.error("Error:", error))
  }

  if (!user){ // Login
    return (
      <div>
        <h1>Login</h1>

        <input
          type="text"
          placeholder="Username"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />

        <br /><br />

        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />

        <br /><br />

        <button onClick={handleLogin}>Login</button>
        <p>{message}</p>
      </div>
    )
  }

  return (
    <div>
      <h1>Enrollment Web App</h1>
      <p>Frontend running</p>

      <button onClick={() => {
        setUser(null)
        setMessage("")
      }}>
        Logout
      </button>

      <div>
        {user.role === "student" && <p>Student Dashboard</p>}
        {user.role === "teacher" && <p>Teacher Dashboard</p>}
      </div>

      <p>{message}</p>

      {roleView === "teacher" && ( // Teacher View Page
        <>
          <h2>Teacher Courses</h2>
          <table>
            <thead>
              <tr>
                <th>Course Name</th>
                <th>Schedule</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {teacherCourses.map((course) => (
                <tr key={course.id}>
                  <td>{course.course_name}</td>
                  <td>{course.schedule}</td>
                  <td>
                    <button onClick={() => loadCourseStudents(course.id)}>
                      View Students
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          <h3>Students in Selected Course</h3>
          <table>
            <thead>
              <tr>
                <th>Student Name</th>
                <th>Grade</th>
                <th>New Grade</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {courseStudents.map((student) => (
                <tr key={student.student_id}>
                  <td>{student.student_name}</td>
                  <td>{student.grade}</td>
                  <td>
                    <input
                      type="number"
                      placeholder="New grade"
                      id={`grade-${student.student_id}`}
                    />
                  </td>
                  <td>
                    <button onClick={() => updateGrade(student.enrollment_id, student.student_id)}>
                      Update Grade
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {roleView === "student" && ( // Student View Page
        <>
          <h2>My Courses</h2>
          <table>
            <thead>
              <tr>
                <th>Course Name</th>
                <th>Schedule</th>
                <th>Grade</th>
              </tr>
            </thead>
            <tbody>
              {studentCourses.map((course) => (
                <tr key={course.course_id}>
                  <td>{course.course_name}</td>
                  <td>{course.schedule}</td>
                  <td>{course.grade}</td>
                </tr>
              ))}
            </tbody>
          </table>
          

          <h2>All Courses</h2>
          <table>
            <thead>
              <tr>
                <th>Course Name</th>
                <th>Schedule</th>
                <th>Enrolled</th>
                <th>Action</th>
              </tr>
            </thead>
            <tbody>
              {courses.map((course) => (
                <tr key={course.id}>
                  <td>{course.course_name}</td>
                  <td>{course.schedule}</td>
                  <td>{course.enrolled_count} / {course.capacity}</td>
                  <td>
                    <button onClick={() => handleEnroll(course.id)}
                      disabled={course.enrolled_count >= course.capacity || isAlreadyEnrolled(course.id)}>
                        {isAlreadyEnrolled(course.id)
                        ? "Enrolled"
                        : course.enrolled_count >= course.capacity
                        ? "Full"
                        : "Enroll"}
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </>
      )}

      {user.role === "admin" && ( // Admin view
        <>
          <h2>Admin Dashboard</h2>

          <iframe
            src="http://127.0.0.1:5000/admin"
            title="Admin Panel"
            width="100%"
            height="600px"
            style={{ border: "none" }}
          />
        </>
      )}

    </div>
  )
}

export default App
# Important Files

## Backend Files

> backend/instance/**enrollment.db**: SQLite database

> app.py: API endpoints 

> dbSetup.py: Database created here (schemas & relationships)

> testDB.py: Insert/test entries into db

## Frontend Files

> App.jsx: Frontend for login (teacher & student), view courses, enroll, update grades

## How to Run
1. Run backend in one terminal: backend/ => python app.py
2. Run frontend in another terminal (go to frontend/ => npm install => npm run dev)
3. Login using account in db

    Example
    - teacher: usrnme - jake123 | password - 1234
    - student: usrnme - jilxio | password - 1234

## Or just use Docker
1. Install docker and make sure you have "docker compose" installed
2. Run `./start.sh` or `docker compose up`
3. Open `http://localhost:5173`

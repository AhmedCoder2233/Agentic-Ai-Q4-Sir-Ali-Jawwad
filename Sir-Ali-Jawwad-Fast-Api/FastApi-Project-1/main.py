from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,constr, EmailStr, validator
from datetime import date

app = FastAPI()

USERS = {}
TASKS = {}


class UserCreate(BaseModel):
    username: str = constr(min_length=3, max_length=20)
    email: EmailStr

class UserRead(BaseModel):
    id: int
    username: str = constr(min_length=3, max_length=20)
    email: EmailStr

class Task(BaseModel):
    id: int
    title: str
    description: str
    status: str 
    due_date: date
    user_id: int

class TaskCreate(BaseModel):
    title: str
    description: str
    status: str
    due_date: date
    user_id: int
    @validator("due_date")
    def check_due_date(cls, value):
        if value < date.today():
            raise ValueError("Due date cannot be in the past.")
        return value

class TaskStatusUpdate(BaseModel):
    status: str

@app.post("/users/")
def createUser(user:UserCreate):
    new_id = max(USERS.keys(), default=0) + 1
    user_data = UserRead(id=new_id, username=user.username, email=user.email)
    USERS[new_id] = user_data
    return user_data

@app.get("/user/{user_id}")
def get_Data(user_id:int):
    if user_id in USERS:
        return USERS[user_id]
    raise HTTPException(status_code=404, detail="User not found")

@app.post("/tasks/")
def createTask(task: TaskCreate):
    new_id = max(TASKS.keys(), default=0) + 1
    new_task = Task(id=new_id, **task.model_dump())
    TASKS[new_id] = new_task
    return new_task

@app.get("/tasks/{task_id}")
def getTask(task_id: int):
    if task_id in TASKS:
        return TASKS[task_id]
    raise HTTPException(status_code=404, detail="Task not found")

@app.put("/tasks/{task_id}")
def update_task_status(task_id: int, status_update: TaskStatusUpdate):
    allowed_status = ["pending", "in_progress", "completed"]

    if task_id not in TASKS:
        raise HTTPException(status_code=404, detail="Task not found")

    if status_update.status not in allowed_status:
        raise HTTPException(status_code=400, detail="Invalid status")

    TASKS[task_id].status = status_update.status
    return TASKS[task_id]

@app.get("/users/{user_id}/tasks")
def listTasks(user_id: int):
    if user_id not in USERS:
        raise HTTPException(status_code=404, detail="User not found")

    user_tasks = [task for task in TASKS.values() if task.user_id == user_id]
    return user_tasks

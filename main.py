from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
from models import ToDoModel
from database import SessionLocal, engine
load_dotenv()  # Load environment variables from .env file


ToDoModel.metadata.create_all(bind=engine)  # Create the todos table in the database

todos = []  # In-memory storage for todos

class ToDoBase(BaseModel):
    title: str
    description: str = None
    completed: bool = False

class ToDoCreate(ToDoBase):
    pass

class ToDoUpdate(ToDoBase):
    pass

class ToDoResponse(ToDoBase):
    id: int

    class Config:
        orm_mode = True
    
def get_db():
    
    db = SessionLocal(bind=engine)
    try:
        yield db
    finally:
        db.close()

app = FastAPI()

@app.get("/todos", response_model=list[ToDoResponse])
async def read_root():
    db = next(get_db())
    todos = db.query(ToDoModel).all()
    return todos


@app.post("/todos", response_model=ToDoResponse)
async def create_todo(todo: ToDoCreate):
    db = next(get_db())
    db_todo = ToDoModel(title=todo.title, description=todo.description, completed=todo.completed)
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.put("/todos/{todo_id}", response_model=ToDoResponse)
async def update_todo(todo_id: int, todo: ToDoUpdate):
    db = next(get_db())
    db_todo = db.query(ToDoModel).filter(ToDoModel.id == todo_id).first()
    if db_todo is None:
        return {"error": "Todo not found"}
    db_todo.title = todo.title
    db_todo.description = todo.description
    db_todo.completed = todo.completed
    db.commit()
    db.refresh(db_todo)
    return db_todo


@app.delete("/todos/{todo_id}")
async def delete_todo(todo_id: int):
    db = next(get_db())
    db_todo = db.query(ToDoModel).filter(ToDoModel.id == todo_id).first()
    if db_todo is None:
        return {"error": "Todo not found"}
    db.delete(db_todo)
    db.commit()
    return {"message": "Todo deleted successfully"}

@app.get("/todos/{todo_id}", response_model=ToDoResponse)
async def get_todo_by_id(todo_id: int):
    db = next(get_db())
    db_todo = db.query(ToDoModel).filter(ToDoModel.id == todo_id).first()
    if db_todo is None:
        return {"error": "Todo not found"}
    return db_todo
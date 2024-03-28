 # fastapi_neon/main.py
# from contextlib import asynccontextmanager
from fastapi import FastAPI,HTTPException
from typing import Union, Optional
from sqlmodel import Field, Session, SQLModel, create_engine, select
from fastapi import FastAPI
from fastapi_neon import settings

class Todo(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    content: str = Field(index=True)

# only needed for psycopg 3 - replace postgresql
# with postgresql+psycopg in settings.DATABASE_URL

connection_string = str(settings.DATABASE_URL).replace(
    "postgresql", "postgresql+psycopg")

# recycle connections after 5 minutes

# to correspond with the compute scale down

engine = create_engine(
    connection_string, connect_args={"sslmode": "require"}, pool_recycle=300)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# The first part of the function, before the yield, will

# be executed before the application starts

# @asynccontextmanager
# async def lifespan(app: FastAPI):
#     print("Creating tables..")
#     create_db_and_tables()
#     yield

app: FastAPI= FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/todos/")
def create_todo(todo: Todo):
    with Session(engine) as session:
        session.add(todo)
        session.commit()
        session.refresh(todo)
        return todo

@app.get("/todos/")
def read_todos():
    with Session(engine) as session:
        todos = session.exec(select(Todo)).all()
        return todos


@app.put("/todos/{todo_id}") 
def update_todo(todo_id: int, todo_update: Todo):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo item not found")
        if todo_update.content:
            todo.content = todo_update.content
        session.commit()
        session.refresh(todo)
        return todo
              

from fastapi import HTTPException

@app.delete("/todos/{todo_id}")
def delete_todo(todo_id: int):
    with Session(engine) as session:
        todo = session.get(Todo, todo_id)
        if not todo:
            raise HTTPException(status_code=404, detail="Todo item not found")
        session.delete(todo)
        session.commit()
        return {"message": "Todo item deleted successfully"}

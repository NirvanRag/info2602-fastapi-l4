from fastapi import APIRouter, HTTPException
from sqlmodel import select
from app.database import SessionDep
from app.models import *
from app.auth import AuthDep
from fastapi import status

category_router = APIRouter(tags=["Category Management"])

@category_router.post("/category", response_model=Category)
def create_category(category: Category, db: SessionDep, user: AuthDep):

    new_category = Category(
        text=category.text,
        user_id=user.id
    )

    db.add(new_category)
    db.commit()
    db.refresh(new_category)

    return new_category

@category_router.post("/todo/{todo_id}/category/{cat_id}")
def add_category_to_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):

    todo = db.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
    ).one_or_none()

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    link = TodoCategory(todo_id=todo_id, category_id=cat_id)

    db.add(link)
    db.commit()

    return {"message": "Category added to todo"}

@category_router.delete("/todo/{todo_id}/category/{cat_id}")
def remove_category_from_todo(todo_id: int, cat_id: int, db: SessionDep, user: AuthDep):

    todo = db.exec(
        select(Todo).where(Todo.id == todo_id, Todo.user_id == user.id)
    ).one_or_none()

    if not todo:
        raise HTTPException(status_code=401, detail="Unauthorized")

    link = db.exec(
        select(TodoCategory).where(
            TodoCategory.todo_id == todo_id,
            TodoCategory.category_id == cat_id
        )
    ).one_or_none()

    if not link:
        raise HTTPException(status_code=404, detail="Category not assigned")

    db.delete(link)
    db.commit()

    return {"message": "Category removed from todo"}

@category_router.get("/category/{cat_id}/todos", response_model=list[TodoResponse])
def get_todos_for_category(cat_id: int, db: SessionDep, user: AuthDep):

    category = db.exec(
        select(Category).where(Category.id == cat_id, Category.user_id == user.id)
    ).one_or_none()

    if not category:
        raise HTTPException(status_code=401, detail="Unauthorized")

    return category.todos
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from backend.app.database import get_db
from backend.app.dependencies import get_current_user
from backend.app.models import User
from backend.app.models.task import Task
from backend.app.schemas.task import TaskCreate, TaskUpdate, TaskResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


@router.post("/", response_model=TaskResponse)
async def create_task(
        task_data: TaskCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    new_task = Task(**task_data.model_dump(), owner_id=current_user.id)
    db.add(new_task)
    await db.commit()
    await db.refresh(new_task)
    return new_task


@router.get("/", response_model=List[TaskResponse])
async def read_tasks(
        skip: int = 0,
        limit: int = 100,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    result = await db.execute(
        select(Task)
        .where(current_user.id == Task.owner_id)
        .offset(skip)
        .limit(limit)
    )

    tasks = result.scalars().all()
    return tasks


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
        task_id: int,
        task_data: TaskUpdate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = await db.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    for key, value in task_data.model_dump(exclude_unset=True).items():
        setattr(task, key, value)

    await db.commit()
    await db.refresh(task)
    return task


@router.delete("/{task_id}")
async def delete_task(
        task_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    task = await db.get(Task, task_id)
    if not task or task.owner_id != current_user.id:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()
    return {"message": "Task deleted"}
from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_uow
from src.core.unitofwork import UnitOfWork
from src.database.models import User
from src.user.schemes import UserCreateScheme, UserScheme, UserUpdateScheme

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/", response_model=list[UserScheme])
async def list_users(uow: UnitOfWork = Depends(get_uow)):
    users = await uow.user.get_all()
    return [UserScheme.model_validate(u) for u in users]


@router.get("/{user_id}", response_model=UserScheme)
async def get_user(user_id: int, uow: UnitOfWork = Depends(get_uow)):
    user = await uow.user.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    return UserScheme.model_validate(user)


@router.post("/", response_model=UserScheme, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreateScheme, uow: UnitOfWork = Depends(get_uow)):
    existing = await uow.user.get_user_by_tg_id(data.telegram_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Пользователь с telegram_id={data.telegram_id} уже существует",
        )
    new_user = User(
        telegram_id=data.telegram_id,
        chat_id=data.chat_id,
        name=data.name,
        lastname=data.lastname,
        email=data.email,
    )
    user = await uow.user.add(new_user)
    await uow.commit()
    return UserScheme.model_validate(user)


@router.patch("/{user_id}", response_model=UserScheme)
async def update_user(
    user_id: int, data: UserUpdateScheme, uow: UnitOfWork = Depends(get_uow)
):
    user = await uow.user.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    updated = await uow.user.update(user_id, data.model_dump(exclude_unset=True))
    await uow.commit()
    return UserScheme.model_validate(updated)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, uow: UnitOfWork = Depends(get_uow)):
    user = await uow.user.get_by_id(user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Пользователь не найден")
    await uow.user.delete(user_id)
    await uow.commit()

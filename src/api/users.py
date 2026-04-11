from fastapi import APIRouter, Depends, HTTPException, status

from src.api.dependencies import get_current_user, get_uow
from src.core.unitofwork import UnitOfWork
from src.database.models import User
from src.user.schemes import UserScheme, UserUpdateScheme

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserScheme)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserScheme.model_validate(current_user)


@router.patch("/me", response_model=UserScheme)
async def update_me(
    data: UserUpdateScheme,
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    updated = await uow.user.update(current_user.id, data.model_dump(exclude_unset=True))
    await uow.commit()
    return UserScheme.model_validate(updated)


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: User = Depends(get_current_user),
    uow: UnitOfWork = Depends(get_uow),
):
    await uow.user.delete(current_user.id)
    await uow.commit()

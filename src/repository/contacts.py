from datetime import datetime, timedelta

from sqlalchemy import select, extract
from sqlalchemy.ext.asyncio import AsyncSession

from src.entity.models import Contact, User
from src.schemas.contacts import ContactSchema, ContactUpdateSchema


async def read_contacts(limit: int, offset: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(user=user).offset(offset).limit(limit)
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts


async def read_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    todo = await db.execute(stmt)
    return todo.scalar_one_or_none()


async def create_contact(body: ContactSchema, db: AsyncSession, user: User):
    stmt = Contact(**body.model_dump(exclude_unset=True), user=user)
    db.add(stmt)
    await db.commit()
    await db.refresh(stmt)
    return stmt


async def update_contact(
    contact_id: int, body: ContactUpdateSchema, db: AsyncSession, user: User
):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact:
        contact.title = body.title
        contact.description = body.description
        contact.completed = body.completed
        await db.commit()
        await db.refresh(contact)
        return contact


async def delete_contact(contact_id: int, db: AsyncSession, user: User):
    stmt = select(Contact).filter_by(id=contact_id, user=user)
    todo = await db.execute(stmt)
    todo = todo.scalar_one_or_none()
    if todo:
        await db.delete(todo)
        await db.commit()
        return todo


async def get_upcoming_birthdays(db: AsyncSession, user: User):
    today = datetime.now().date()
    next_week = today + timedelta(days=7)
    stmt = (
        select(Contact)
        .filter_by(user=user)
        .where(
            (
                extract("month", Contact.birthday)
                == today.month & extract("day", Contact.birthday)
                >= today.day
            )
            | (
                extract("month", Contact.birthday)
                == next_week.month & extract("day", Contact.birthday)
                < today.day
            )
        )
    )
    result = await db.execute(stmt)
    contacts = result.scalars().all()
    return contacts

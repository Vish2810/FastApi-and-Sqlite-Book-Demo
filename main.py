from fastapi import FastAPI, Response, status, HTTPException, Depends
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from pydantic import BaseModel, Field
import models
from uvicorn import run

app = FastAPI(title="BOOK CLUB")

models.Base.metadata.create_all(bind=engine)


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


class Books(BaseModel):
    title: str = Field(min_length=1)
    author: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=100)
    rating: int = Field(gt=1, lt=101)


BOOKS = []


@app.get("/")
def read_books(db: Session = Depends(get_db)):
    read = db.query(models.Books).all()
    return read


@app.post("/")
def create_book(book: Books, db: Session = Depends(get_db)):
    book_model = models.Books()
    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating
    db.add(book_model)
    db.commit()
    return book


@app.put("/{book_id}")
def update_book(book_id: int, book: Books, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == book_id).first()

    if book_model is None:
        raise HTTPException(
            status_code=404,
            detail=f"{book_id} :book does not exist")

    book_model.title = book.title
    book_model.author = book.author
    book_model.description = book.description
    book_model.rating = book.rating
    db.add(book_model)
    db.commit()
    db.refresh
    return book


@app.delete("/{book_id}")
def delete_book(book_id: int, db: Session = Depends(get_db)):
    book_model = db.query(models.Books).filter(models.Books.id == book_id).delete()
    db.commit()


if __name__ == '__main__':
    run("main:app", host="0.0.0.0", port=5023, reload=True)

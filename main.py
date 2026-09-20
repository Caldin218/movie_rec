from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, relationship
from database import get_db
from models import Movie, Rating, User
from pydantic import BaseModel, Field, ConfigDict

#=============================  SCHEMA MOVIE  =======================================

class MovieCreate(BaseModel):
    title: str

class MovieResponse(BaseModel):
    id: int
    title: str

    model_config= ConfigDict(from_attributes=True) #Cho phép TRUE: Pydantic nhận/tiếp xúc attributes từ Objects của SqlAlchemy 
#=============================  SCHEMA RATING  =======================================
class RatingCreate(BaseModel):
    user_id: int
    movie_id: int
    rating: int = Field(ge= 1, le= 5)

class RatingResponse(BaseModel):
    id: int
    user_id: int
    movie_id: int
    rating: int

    model_config = ConfigDict(from_attributes=True) #Cho phép TRUE: Pydantic lấy các attributes của Objects đầu vào 

class RatingUpdate(BaseModel):
    rating: int = Field(ge= 1, le= 5)
#=============================  SCHEMA USER  =======================================

class UserCreate(BaseModel):
    email : str
    password_hash : str

class UserResponse(BaseModel):
    id: int
    email: str


#===================================================================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#=============================  ENDPOINTS  =======================================
@app.get("/")
def home():
    return {"message": "Movie Recommendation Platform is running!"}
#=============================  MOVIES  =======================================
@app.get("/movies", response_model= list[MovieResponse])
def get_movies(db: Session = Depends(get_db)):
    return db.query(Movie).all()

@app.get("/movies/{id}", response_model= MovieResponse)
def get_movies_by_id(id: int, db: Session = Depends(get_db)):

    existing_movie = db.get(Movie, id)

    if existing_movie:
        return existing_movie

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )

@app.post("/movies", response_model= MovieResponse)
def create_movie(movie: MovieCreate, db: Session = Depends(get_db)):
    db_movie = Movie(title = movie.title)
    db.add(db_movie)
    db.commit()
    return db_movie

@app.put("/movies/{id}", response_model= MovieResponse)
def update_movie_by_id(id: int, movie: MovieCreate, db: Session = Depends(get_db)):

    existing_movie = db.get(Movie, id)

    if existing_movie:

        existing_movie.title = movie.title

        db.commit()

        return existing_movie

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )

@app.delete("/movies/{id}", status_code=204)
def delete_movie_by_id(id: int, db: Session = Depends(get_db)):
    existing_movie = db.get(Movie, id)

    if existing_movie:

        db.delete(existing_movie)

        db.commit()

        return

    raise HTTPException(
        status_code=404,
        detail="Movie not found"
    )

#=============================  RATINGS  =======================================
@app.get("/ratings", response_model= list[RatingResponse])
def get_ratings(db: Session = Depends(get_db)):
    return db.query(Rating).all()

@app.post("/ratings", response_model= RatingResponse)
def create_rating(rating: RatingCreate, db: Session = Depends(get_db)):

    existing_user = db.get(User, rating.user_id)

    existing_movie = db.get(Movie, rating.movie_id)

    existing_rating = db.query(Rating).filter(
        Rating.user_id == rating.user_id,
        Rating.movie_id == rating.movie_id
    ).first()

    if not existing_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not existing_movie:
        raise HTTPException(
            status_code=404,
            detail="Movie not found"
        )

    if existing_rating:

        existing_rating.rating = rating.rating

        db.commit()     

        return existing_rating

    else:
        
        db_rating = Rating(user_id = rating.user_id, movie_id = rating.movie_id, rating = rating.rating)

        db.add(db_rating)

        db.commit()

        return db_rating

@app.put("/ratings/{id}", response_model= RatingResponse)
def update_rating_by_id(id: int, rating: RatingUpdate, db: Session = Depends(get_db)):

    existing_rating = db.get(Rating, id)

    if existing_rating:

        existing_rating.rating = rating.rating

        db.commit()

        return existing_rating

    raise HTTPException(
        status_code=404,
        detail="Not found rating"
    )

@app.delete("/ratings/{id}", status_code=204)
def delete_rating_by_id(id: int, db: Session = Depends(get_db)):

    existing_rating = db.get(Rating, id)

    if existing_rating:

        db.delete(existing_rating)

        db.commit()

        return 

    raise HTTPException(
        status_code= 404,
        detail="Rating not found"
    )

#=============================  USERS  ======================================
@app.get("/users", response_model= list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

@app.get("/users/{id}", response_model= UserResponse)
def get_user_by_id(id: int, db: Session = Depends(get_db)):

    existing_user = db.get(User,id)

    if existing_user:
        return existing_user

    raise HTTPException(status_code=404,  detail="User not found")

@app.post("/users", response_model= UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):

    existing_email = db.query(User).filter(User.email == user.email).first()

    if existing_email:

        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    db_user = User(email = user.email, password_hash = user.password_hash)

    try: 

        db.add(db_user)

        db.commit()

        db.refresh(db_user)

    except IntegrityError as e:

        db.rollback()

        print("Orgin Error: ", e.orig)

        raise HTTPException(
            status_code=409,
            detail="Database Integrity Constraint violated"
        )

    return db_user

@app.put("/users/{id}", response_model= UserResponse)
def update_user_by_id(id:int, user: UserCreate, db: Session= Depends(get_db)):

    existing_user = db.get(User, id)

    if existing_user:

        check_email_dup = db.query(User).filter((User.email == user.email) & (User.id != id)).first()

        if check_email_dup:
            raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

        existing_user.email = user.email

        existing_user.password_hash = user.password_hash

        try:

            db.commit()

        except IntegrityError as e:

            db.rollback()
            print("Origin Error:", e.orig)

            raise HTTPException(
                status_code=409,
                detail="Database integrity constraint violated"
            )

        return existing_user

    raise HTTPException(
        status_code= 404,
        detail="User not found"
    )

@app.delete("/users/{id}", status_code= 204)
def delete_user_by_id(id: int, db: Session = Depends(get_db)):

    existing_user = db.get(User, id)

    if existing_user:
        db.delete(existing_user)

        db.commit()

        return

    raise HTTPException(status_code=404, detail="User not found")
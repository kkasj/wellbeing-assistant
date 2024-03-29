from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.database_modules.database import db
from api.database_modules.entities import *
from api.routers import auth, users, meals, surveys, exercises, recommendations


app = FastAPI(
    title="Well-being Assistant API",
    debug = True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

db.connect()

db.create_tables([Exercise, Meal, Survey, SurveyAnswer, SurveyQuestion, Question, User, UserExercise, UserMeal], safe=True)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(meals.router)
app.include_router(exercises.router)
app.include_router(surveys.router)
app.include_router(recommendations.router)
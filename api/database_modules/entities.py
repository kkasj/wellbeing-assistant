from peewee import Model, SqliteDatabase, CharField, ForeignKeyField, IntegerField, FloatField, ManyToManyField, DateTimeField, DateField
import datetime
from .database import db
import json

class BaseModel(Model):
    class Meta:
        database = db
        
class Exercise(BaseModel):
    name = CharField()
    exercise_type = IntegerField() #enum ExerciseType
    category = CharField()
    
class Meal(BaseModel):
    name = CharField()
    health_index = IntegerField()
    glycemic_index = IntegerField()
    protein = FloatField()
    carbohydrates = FloatField()
    fats = FloatField()
    fiber = FloatField()
    meal_type = IntegerField() #enum MealType
    
class Survey(BaseModel):
    name = CharField()
    survey_type = IntegerField()  #enum SurveyType  "post-meal" / "post-exercise" / "well-being"
    
class Question(BaseModel):
    question_content = CharField()
    
# many to many relationship between question and survey
class SurveyQuestion(BaseModel):
    survey = ForeignKeyField(Survey) 
    question = ForeignKeyField(Question)
    

class SurveyAnswer(BaseModel):
    survey = ForeignKeyField(Survey)
    question = ForeignKeyField(Question)
    answer_score = IntegerField()
    activity_id = IntegerField()
    activity_type = IntegerField() #enum ActivityType
    
class User(BaseModel):
    name = CharField()
    email = CharField(unique = True)
    password_hash = CharField()
    
class UserExercise(BaseModel):
    user = ForeignKeyField(User)
    exercise = ForeignKeyField(Exercise)
    date = DateTimeField(default=datetime.datetime.now)
    time = IntegerField(null = True) # in minutes
    repetitions = IntegerField(null = True)

class UserMeal(BaseModel):
    user = ForeignKeyField(User)
    meal = ForeignKeyField(Meal)
    date = DateTimeField(default=datetime.datetime.now)
    weight = IntegerField() # in grams


def create_tables():
    with db:
        db.create_tables([User, UserMeal, UserExercise, Survey, Question, SurveyAnswer, Meal, Exercise])

        with open('api/data/meals.json') as f:
            meals = json.load(f)
            for meal in meals:
                Meal.create(name=meal['name'], health_index=meal['health_index'], glycemic_index=meal['glycemic_index'], protein=meal['protein'], carbohydrates=meal['carbohydrates'], fats=meal['fats'], fiber=meal['fiber'], meal_type=meal['meal_type'])
        
        with open('api/data/exercises.json') as f:
            exercises = json.load(f)
            for exercise in exercises:
                Exercise.create(name=exercise['name'], exercise_type=exercise['exercise_type'], category=exercise['category'])
        
    
def drop_tables():
    with db:
        db.drop_tables([User, UserMeal, UserExercise, Survey, Question, SurveyAnswer, Meal, Exercise])
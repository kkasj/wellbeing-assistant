from fastapi import APIRouter, Query, Path, Depends, Body, Form, HTTPException
from peewee import *

from api.models import Token, UserDto, UserMealDto, MealDto, UserCompositeMealDto, UserExerciseDto, SurveyAnswerRequest, ActivityDetailsRequest, Activity
from api.auth.jwt_handler import validate_token
from api.database_modules.entities import User, UserMeal, UserExercise, Survey, Question, SurveyAnswer, Meal, Exercise, SurveyQuestion
from api.enums import ActivityType, SurveyType
from api.routers.users import get_activities
import datetime

from recommendation_model import interface as rec_interface



router = APIRouter(
    prefix="/recommendations",
)

@router.get('/meal', response_model=UserMealDto, tags=['recommendations'])
def get_meal_recommendation(user: UserDto = Depends(validate_token)):
    '''
    Returns a meal recommendation for the user
    '''

    meal_history = get_user_meal_history(user)
    available_meals = get_available_meals()
    
    recommended_meal, weight, wellbeing_score = rec_interface.get_meal_recommendation(meal_history, available_meals)

    # recommended meal is now a dictionary with the meal and the weight
    # turn the recommended meal into a UserCompositeMealDto
    recommended_meal = MealDto(meal_id=recommended_meal['id'], weight=weight)

    return recommended_meal


@router.get('/exercise', response_model=UserExerciseDto, tags=['recommendations'])
def get_exercise_recommendation(user: UserDto = Depends(validate_token)):
    '''
    Returns an exercise recommendation for the user
    '''


def _query_to_value(query):
    if len(query) == 0:
        return None
    return query[0]


def get_user_meal_history(user: UserDto):
    activities = get_activities(user)
    meals_activities = [activity for activity in activities if activity.activity_type == ActivityType.MEAL]
    meals_activities_ids = [meal.activity_id for meal in meals_activities]

    meal_questions = _get_meal_survey_questions()

    survey_answers = []
    filtered_activities_ids = []
    for activity_id in meals_activities_ids:
        activity_survey_answers = SurveyAnswer.select().where(SurveyAnswer.activity_id == activity_id)
        if len(activity_survey_answers) == 0:
            continue
        
        question_answers = [_query_to_value(activity_survey_answers.where(SurveyAnswer.question == question.id).limit(1)) for question in meal_questions]

        if None in question_answers:
            continue

        survey_answers.append(question_answers)
        filtered_activities_ids.append(activity_id)

    # take only the meals for which we have survey answers
    user_meals: list[UserMeal] = [_query_to_value(UserMeal.select().where(UserMeal.id == activity_id).limit(1)) for activity_id in filtered_activities_ids]
    user_meals_with_survey_answers: list[dict] = [_user_meal_to_dict(user_meal, answers) for user_meal, answers in zip(user_meals, survey_answers)]

    return user_meals_with_survey_answers


def get_available_meals():
    available_meals: list[Meal] = list(Meal.select())
    available_meals: list[dict] = [_meal_to_dict(meal) for meal in available_meals]
    
    return available_meals

def _get_meal_survey_questions():
    meal_survey = list(Survey.select().where(Survey.survey_type == str(SurveyType.MEAL.value)).limit(1))[0]
    meal_survey_questions = list(SurveyQuestion.select().where(SurveyQuestion.survey == meal_survey.id))
    meal_questions_ids = [question.question for question in meal_survey_questions]
    meal_questions = list(Question.select().where(Question.id << meal_questions_ids))

    return meal_questions


def _user_meal_to_dict(user_meal, survey_answers):
    result = {
        "id": user_meal.meal.id,
        "name": user_meal.meal.name,
        "health_index": user_meal.meal.health_index,
        "glycemic_index": user_meal.meal.glycemic_index,
        "protein": user_meal.meal.protein,
        "carbohydrates": user_meal.meal.carbohydrates,
        "fats": user_meal.meal.fats,
        "fiber": user_meal.meal.fiber,
        "meal_type": user_meal.meal.meal_type,
        "weight": user_meal.weight,
    }

    result.update(_survey_answers_to_dict(survey_answers))

    return result

def _meal_to_dict(meal):
    return {
        "id": meal.id,
        "name": meal.name,
        "health_index": meal.health_index,
        "glycemic_index": meal.glycemic_index,
        "protein": meal.protein,
        "carbohydrates": meal.carbohydrates,
        "fats": meal.fats,
        "fiber": meal.fiber,
        "meal_type": meal.meal_type,
    }

def _survey_answers_to_dict(survey_answers):
    return {
        f"question_{answer.question.id}": answer.answer_score
        for answer in survey_answers
    }
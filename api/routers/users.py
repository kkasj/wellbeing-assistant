from fastapi import APIRouter, Query, Path, Depends, Body, Form, HTTPException
from peewee import *

from api.models import Token, UserDto, UserMealDto, UserCompositeMealDto, UserExerciseDto, SurveyAnswerRequest, ActivityDetailsRequest, Activity
from api.auth.jwt_handler import pwd_context, create_access_token, oauth2_scheme, validate_token, get_password_hash, verify_password, authenticate_user
from api.database_modules.entities import User, UserMeal, UserExercise, Survey, Question, SurveyAnswer, Meal, Exercise
from api.enums import ActivityType, SurveyType
# from api.routers.recommendations import _get_meal_survey_questions, _survey_answers_to_dict

from recommendation_model.interface import update_meal_model


router = APIRouter(
    prefix="/users",
    tags=["users"],
)

@router.get('/me', tags=['users'], response_model=UserDto)
async def get_me(user: UserDto = Depends(validate_token)):
    '''
    Get the current user
    '''
    return user

@router.post('/meal', tags=['users'], response_model=bool)
async def add_meal_to_user(user_composite_meal_dto : UserCompositeMealDto, user: UserDto = Depends(validate_token)):
    '''
    Adds a meal to the user meal history
    '''
    for meal in user_composite_meal_dto.meals:
        __add_meal_to_user(user, meal)
    return True

@router.post('/exercise', tags=['users'], response_model=bool)
async def add_exercise_to_user(user_exercise_dto : UserExerciseDto, user: UserDto = Depends(validate_token)):
    '''
    Adds an exercise to the user exercise history
    '''
    __add_exercise_to_user(user, user_exercise_dto)
    return True


@router.post('/survey', tags=['users'], response_model=bool)
async def add_survey_answers_to_user(survey_answer_request : SurveyAnswerRequest, user: UserDto = Depends(validate_token)):
    '''
    Adds survey answers to the user survey history
    '''

    # activities = get_activities(user)

    # if activities is None or len(activities) == 0:
    #     raise HTTPException(status_code=404, detail="No recent activities found")

    # most_recent_activity = activities[0]

    survey_answers = __add_survey_answers_to_user(user, survey_answer_request)
    # survey_type = survey_answers[0].survey.survey_type

    # match survey_type:
    #     case SurveyType.MEAL:
    #         meal_questions = _get_meal_survey_questions()
    #         survey_answers = sorted(survey_answers, key=lambda x: meal_questions.index(x.question_id))

    #         user_meal_history = [meal.to_dict() for meal in get_activities_meals(user)[1:11]]

    #         update_meal_model(user_meal_history, )
    #     case SurveyType.EXERCISE:
    #         pass

    return True

@router.get('/history', tags=['users'], response_model=list[Activity])
async def get_user_history(user: UserDto = Depends(validate_token)):
    '''
    Get user history, the list of meals and exercises
    '''
    return get_activities(user)


def __add_meal_to_user(user: UserDto, user_meal_dto : UserMealDto):
    try:
        Meal.get(Meal.id == user_meal_dto.meal_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Meal not found")
    
    UserMeal.create(
        user_id = user.id,
        meal_id = user_meal_dto.meal_id,
        weight = user_meal_dto.weight
    )
    
def __add_exercise_to_user(user: UserDto, user_exercise_dto : UserExerciseDto):
    try:
        Exercise.get(Exercise.id == user_exercise_dto.exercise_id)
    except DoesNotExist:
        raise HTTPException(status_code=404, detail="Exercise not found")
    
    UserExercise.create(
        user_id = user.id,
        exercise_id = user_exercise_dto.exercise_id,
        time = user_exercise_dto.time,
        repetitions = user_exercise_dto.repetitions
    )
    
def __add_survey_answers_to_user(user: UserDto, survey_answer_request : SurveyAnswerRequest) -> list[SurveyAnswer]:
    recent_activities = get_activities(user)
    if recent_activities == None or len(recent_activities) == 0:
        raise HTTPException(status_code=404, detail="No recent activities found")
    most_recent_activity = recent_activities[0]
    
    survey_answers = []    
    for survey_answer in survey_answer_request.list_of_answers:
        try:
            Survey.get(Survey.id == survey_answer.survey_id)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Survey not found")
        
        try:
            Question.get(Question.id == survey_answer.question_id)
        except DoesNotExist:
            raise HTTPException(status_code=404, detail="Question not found")
        
        survey_answer = SurveyAnswer.create(
            survey_id = survey_answer.survey_id,
            question_id = survey_answer.question_id,
            answer_score = survey_answer.answer_score,
            activity_id = most_recent_activity.activity_id,
            activity_type = most_recent_activity.activity_type.value
        )

        survey_answers.append(survey_answer)
    
    return survey_answers

def __get_user_meals(user: UserDto):
    return (UserMeal
            .select(UserMeal, Meal)
            .join(Meal)
            .where(UserMeal.user_id == user.id))

def __get_user_exercises(user: UserDto):
    return (UserExercise
            .select(UserExercise, Exercise)
            .join(Exercise)
            .where(UserExercise.user_id == user.id))

def get_activities(user: UserDto) -> list[Activity]:
    meals = __get_user_meals(user)
    exercises = __get_user_exercises(user)
    if meals.count() == 0 and exercises.count() == 0:
        return []
    activities = []
    for meal in meals:
        activities.append(Activity(
            activity_id = meal.id,
            activity_name = meal.meal.name,
            activity_type = ActivityType.MEAL,
            date = meal.date
        ))
    for exercise in exercises:
        activities.append(Activity(
            activity_id = exercise.id,
            activity_name = exercise.exercise.name,
            activity_type = ActivityType.EXERCISE,
            date = exercise.date
        ))
    activities.sort(key=lambda x: x.date, reverse=True)
    return activities
    
def get_activities_meals(user: UserDto) -> list[UserMeal]:
    meals = list(__get_user_meals(user))
    meals.sort(key=lambda x: x.date, reverse=True)

    return meals

def get_activities_exercises(user: UserDto) -> list[UserExercise]:
    exercises = list(__get_user_exercises(user))
    exercises.sort(key=lambda x: x.date, reverse=True)

    return exercises
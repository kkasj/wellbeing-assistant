import numpy as np

from keras.models import load_model
from recommendation_model.preprocessing import *


def load_meal_model():
    return load_model('recommendation_model/meal_model.h5')

def load_exercise_model():
    return load_model('recommendation_model/exercise_model.h5')


def save_meal_model(model):
    model.save('recommendation_model/meal_model.h5')

def save_exercise_model(model):
    model.save('recommendation_model/exercise_model.h5')


def get_wellbeing_scores(model, preprocessed_user_meal_history: np.ndarray, preprocessed_available_meals: np.ndarray):
    wellbeing_scores = []

    for meal in preprocessed_available_meals:
        wellbeing_score = model.predict([preprocessed_user_meal_history, meal], verbose=0)
        wellbeing_scores.append(wellbeing_score[0, 0])

    return wellbeing_scores


def get_meal_recommendation(user_meal_history: list[dict], available_meals: list[dict]):
    model = load_meal_model()

    preprocessed_user_meal_history = preprocess_meal_history(user_meal_history)
    preprocessed_available_meals = [preprocess_meal_target(meal) for meal in available_meals]

    wellbeing_scores = get_wellbeing_scores(model, preprocessed_user_meal_history, preprocessed_available_meals)

    best_meal_ind = np.argmax(wellbeing_scores)
    best_meal = available_meals[best_meal_ind]
    best_meal_score = wellbeing_scores[best_meal_ind]

    return (best_meal, best_meal_score)


def update_meal_model(user_meal_history: list[dict], meal: dict, wellbeing_score: float):
    model = load_meal_model()

    preprocessed_user_meal_history = preprocess_meal_history(user_meal_history)
    preprocessed_meal = preprocess_meal_target(meal)

    model.fit([preprocessed_user_meal_history, preprocessed_meal], [wellbeing_score], epochs=1, batch_size=1, verbose=0)

    save_meal_model(model)
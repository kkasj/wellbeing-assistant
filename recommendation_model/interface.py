import keras.preprocessing

from keras.models import load_model
from recommendation_model.preprocessing import *


def load_model_meals():
    return load_model('recommendation_model/model_meals.h5')

def load_model_exercises():
    return load_model('recommendation_model/model_exercises.h5')


def save_model_meals(model):
    model.save('recommendation_model/model_meals.h5')

def save_model_exercises(model):
    model.save('recommendation_model/model_exercises.h5')


def get_wellbeing_score(model, user_meal_history, user_meal):
    user_meal_history = preprocess_meal_history(user_meal_history)
    user_meal = preprocess_meal_target(user_meal)

    well_being_score = model.predict([user_meal_history.to_numpy().reshape(1, 10, 12), user_meal.to_numpy().reshape(1, 7)])

    return well_being_score


def get_meal_recommendation(user_meal_history, available_meals):
    model = load_model_meals()

    # preprocess the meal history
    user_meal_history = preprocess_meal_history(user_meal_history)

    mu = user_meal_history['weight'].mean()
    sigma = user_meal_history['weight'].std()

    user_meal_history = user_meal_history.to_numpy().reshape(1, -1, 12)
    user_meal_history = keras.preprocessing.sequence.pad_sequences(user_meal_history, maxlen=10, padding='post', truncating='post')

    # iterate through each meal in available_meals
    # and 5 weights for each meal, between mu - 2*sigma and mu + 2*sigma, where mu is the mean and sigma is the standard deviation for the weights in meal history
    # and calculate the well-being score for each meal
    best_user_meal = None
    best_user_meal_weight = None
    best_user_meal_score = None
    for meal in available_meals:
        for i in range(5):
            user_meal = meal.copy()
            weight = mu - 2*sigma + (i/4) * 4*sigma
            user_meal['weight'] = weight
            user_meal = preprocess_meal_target(user_meal)

            well_being_score = model.predict([user_meal_history, user_meal.to_numpy().reshape(1, 7)])

            if best_user_meal_score is None or well_being_score > best_user_meal_score:
                best_user_meal = meal
                best_user_meal_weight = weight
                best_user_meal_score = well_being_score


    return (best_user_meal, best_user_meal_weight, best_user_meal_score[0][0])


# def feedback()
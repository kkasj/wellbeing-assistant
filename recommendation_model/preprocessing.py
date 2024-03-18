import pandas as pd
import numpy as np
import keras

from api.enums import MealType, ExerciseType, ExerciseCategory
from api.database_modules.entities import UserMeal, Exercise

def preprocess_meal_history(meals: list[dict]) -> np.ndarray:
    if len(meals) == 0:
        return np.zeros((1, 10, 12))

    meal_history_df = pd.DataFrame(meals)
    meal_history_df = meal_history_df.drop(columns=["id", "meal_type", "name"])

    # normalize weight
    meal_history_df["weight"] = meal_history_df["weight"] / meal_history_df["weight"].max()

    meal_history = meal_history_df.to_numpy().reshape(1, -1, 12)
    meal_history = keras.preprocessing.sequence.pad_sequences(meal_history, maxlen=10, padding='post', truncating='pre')

    return meal_history

def preprocess_meal_target(meal: dict) -> np.ndarray:
    meal_df = pd.DataFrame([meal])
    meal_df = meal_df.drop(columns=["id", "meal_type", "name"])

    meal = meal_df.to_numpy().reshape(1, 6)

    return meal

def preprocess_exercises(exercises: dict):
    exercises_df = pd.DataFrame(exercises)
    exercises_df = exercises_df.drop(columns=["id", "exercise_type", "name"])

    # change the category to its name
    exercises_df["category"] = exercises_df["category"].apply(lambda x: ExerciseCategory(x).name.lower())

    # deal with exercises categories - one hot encoding - categories: cardio, strength, flexibility, balance, functional
    exercises_df = pd.get_dummies(exercises_df, columns=["category"], prefix='', prefix_sep='')
    
    
    # combine time and repetitions into one column - intensity
    # first normalize the time and repetitions
    # then add them together

    # normalization
    if exercises_df["time"].max() == 0:
        exercises_df["time"] = 0
    else:
        exercises_df["time"] = exercises_df["time"] / exercises_df["time"].max()
    
    if exercises_df["repetitions"].max() == 0:
        exercises_df["repetitions"] = 0
    else:
        exercises_df["repetitions"] = exercises_df["repetitions"] / exercises_df["repetitions"].max() or 0

    # add them together
    exercises_df["intensity"] = exercises_df["time"] + exercises_df["repetitions"]

    # drop the original time and repetitions columns
    exercises_df = exercises_df.drop(columns=["time", "repetitions"])

    return exercises_df




def combine_activities(meals_df: pd.DataFrame, exercises_df: pd.DataFrame):
    # combine meals and exercises into one dataframe for training
    # add a column to indicate if it's a meal or an exercise
    # 1 for meal, 0 for exercise
    # fill in the missing values with 0

    meals_df["is_meal"] = 1
    exercises_df["is_meal"] = 0

    combined_df = pd.concat([meals_df, exercises_df], ignore_index=True)
    combined_df = combined_df.fillna(0)

    return combined_df
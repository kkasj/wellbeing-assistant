import keras

from keras.layers import Input, LSTM, Dense, Embedding, Flatten, Concatenate, Dropout, Masking, concatenate
from keras.optimizers import Adam

from keras.models import Model
from api.enums import MealType, ExerciseType
from api.database_modules.entities import UserMeal, UserExercise, Meal, Exercise
from api.routers.recommendations import get_user_meal_history, get_available_meals


def build_meal_model():
    # Configuration parameters
    sequence_length = 10  # Example sequence length of meal history
    num_features = 12  # Number of features per meal, adjust based on your actual feature set
    num_meal_features = 6  # Assuming the specific meal uses the same feature set

    # Inputs
    historical_meals_input = Input(shape=(sequence_length, num_features), name='historical_meals')
    specific_meal_input = Input(shape=(num_meal_features,), name='specific_meal')

    # Mask historical meals
    historical_meals_input = Masking(mask_value=0.0)(historical_meals_input)

    # Historical meals pathway
    lstm_out = LSTM(64)(historical_meals_input)
    lstm_dropout = Dropout(0.5)(lstm_out)

    # Specific meal pathway
    specific_meal_dense = Dense(64, activation='relu')(specific_meal_input)
    specific_meal_dropout = Dropout(0.5)(specific_meal_dense)

    # Merge pathways
    merged = concatenate([lstm_dropout, specific_meal_dropout])

    # Further processing
    merged_dense = Dense(64, activation='relu')(merged)
    output_dropout = Dropout(0.5)(merged_dense)

    # Output layer for well-being score prediction
    well_being_score = Dense(1, activation='linear', name='well_being_output')(output_dropout)

    # Compile the model
    model = Model(inputs=[historical_meals_input, specific_meal_input], outputs=well_being_score)
    model.compile(optimizer=Adam(), loss='mse', metrics=['mae'])

    # Model summary
    # model.summary()

    return model


def build_exercise_model():
    # Configuration parameters
    sequence_length = 10  # Example sequence length of meal history
    num_features = 12  # Number of features per meal, adjust based on your actual feature set
    num_exercise_features = 2  # Assuming the specific meal uses the same feature set

    # Inputs
    historical_exercises_input = Input(shape=(sequence_length, num_features), name='historical_exercises')
    specific_exercise_input = Input(shape=(num_exercise_features,), name='specific_exercise')

    # Mask historical exercises
    historical_exercises_input = Masking(mask_value=0.0)(historical_exercises_input)

    # Historical exercises pathway
    lstm_out = LSTM(64)(historical_exercises_input)
    lstm_dropout = Dropout(0.5)(lstm_out)

    # Specific exercise pathway
    specific_exercise_dense = Dense(64, activation='relu')(specific_exercise_input)
    specific_exercise_dropout = Dropout(0.5)(specific_exercise_dense)

    # Merge pathways
    merged = concatenate([lstm_dropout, specific_exercise_dropout])

    # Further processing
    merged_dense = Dense(64, activation='relu')(merged)
    output_dropout = Dropout(0.5)(merged_dense)

    # Output layer for well-being score prediction
    well_being_score = Dense(1, activation='linear', name='well_being_output')(output_dropout)

    # Compile the model
    model = Model(inputs=[historical_exercises_input, specific_exercise_input], outputs=well_being_score)
    model.compile(optimizer=Adam(), loss='mse', metrics=['mae'])

    # Model summary
    # model.summary()

    return model


def pretrain_meal_model(model, X_train_meal_history, X_train_meal, y_train):
    # Pad the meal history sequences to a fixed length of 10
    X_train_meal_history = keras.preprocessing.sequence.pad_sequences(X_train_meal_history, maxlen=10, padding='post', truncating='post')
    
    # Pre-training the meal model
    history = model.fit([X_train_meal_history, X_train_meal], y_train, epochs=20, batch_size=1, validation_split=0.2, verbose=1)

    return history

def pretrain_exercise_model(model, X_train_exercise_history, X_train_exercise, y_train):
    # Pad the exercise history sequences to a fixed length of 10
    X_train_exercise_history = keras.preprocessing.sequence.pad_sequences(X_train_exercise_history, maxlen=10, padding='post', truncating='post')
    
    # Pre-training the exercise model
    history = model.fit([X_train_exercise_history, X_train_exercise], y_train, epochs=20, batch_size=1, validation_split=0.2, verbose=1)

    return history


# def prepare_data_for_meal_model_pretraining():
#     available_meals = get_available_meals()

def create_model():
    model = build_meal_model()
    model.save('recommendation_model/meal_model.h5')


if __name__ == '__main__':
    create_model()
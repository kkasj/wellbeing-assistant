from enum import Enum, auto

class MealType(Enum):
    INGREDIENT = auto()
    PREPERED_MEAL = auto()
    
class ExerciseType(Enum):
    REPETITIONS = auto()
    TIMED = auto()
    
class SurveyType(Enum):
    MEAL = auto()
    #POST_MEAL = auto()
    EXERCISE = auto()
    #POST_EXERCISE = auto()
    #WELL_BEING = auto()
    NONE = auto()
    
class ActivityType(Enum):
    MEAL = auto()
    EXERCISE = auto()
    

class ExerciseCategory(Enum):
    CARDIO = auto()
    STRENGTH = auto()
    FLEXIBILITY = auto()
    BALANCE = auto()
    FUNCTIONAL = auto()
    
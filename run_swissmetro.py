import pandas as pd

from choice_jev import ask_jev

from config import (
    GROUP_MAP,
    SURVEY_MAP,
    SP_MAP,
    PURPOSE_MAP,
    FIRST_MAP,
    TICKET_MAP,
    WHO_MAP,
    LUGGAGE_MAP,
    AGE_MAP,
    GENDER_MAP,
    INCOME_MAP,
    GA_MAP,
    CANTON_MAP,
    SM_SEATS_MAP,
    decode,
)
# ============================================================
# 1. 读取 Swissmetro 数据
# ============================================================

csv_path = "data/raw/swissmetro.csv"

df = pd.read_csv(csv_path)

print("Dataset shape:", df.shape)
print(df.head())


# ============================================================
# 2. 把一行 Swissmetro 数据转换成 JEV state
# ============================================================

def row_to_state(row):

    state = {
        "traveler": {
            #"population_group": decode(GROUP_MAP, row["GROUP"]),
            "survey_source": decode(SURVEY_MAP, row["SURVEY"]),
            #"survey_type": decode(SP_MAP, row["SP"]),
            "respondent_id": int(row["ID"]),

            "travel_purpose": decode(PURPOSE_MAP, row["PURPOSE"]),
            "travel_class": decode(FIRST_MAP, row["FIRST"]),
            "ticket_type": decode(TICKET_MAP, row["TICKET"]),
            "who_pays": decode(WHO_MAP, row["WHO"]),

            "luggage": decode(LUGGAGE_MAP, row["LUGGAGE"]),
            "age_group": decode(AGE_MAP, row["AGE"]),
            "gender": decode(GENDER_MAP, row["MALE"]),
            "annual_income": decode(INCOME_MAP, row["INCOME"]),
            "ga_travelcard": decode(GA_MAP, row["GA"]),
        },

        "trip": {
            "origin": decode(CANTON_MAP, row["ORIGIN"]),
            "destination": decode(CANTON_MAP, row["DEST"]),
        },

        "alternatives": {

            "train": {
                "available": bool(row["TRAIN_AV"]),
                "travel_time_minutes": float(row["TRAIN_TT"]),
                "cost_chf": float(row["TRAIN_CO"]),
                "headway_minutes": float(row["TRAIN_HE"]),
            },

            "swissmetro": {
                "available": bool(row["SM_AV"]),
                "travel_time_minutes": float(row["SM_TT"]),
                "cost_chf": float(row["SM_CO"]),
                "headway_minutes": float(row["SM_HE"]),
                "seat_configuration": decode(
                    SM_SEATS_MAP,
                    row["SM_SEATS"]
                ),
            },

            "car": {
                "available": bool(row["CAR_AV"]),
                "travel_time_minutes": float(row["CAR_TT"]),
                "cost_chf": float(row["CAR_CO"]),
            },
        },
    }

    return state

def row_to_questions(row):

    criteria = {}

    if row["TRAIN_AV"] == 1:
        criteria["train"] = "The traveler chooses conventional train."

    if row["SM_AV"] == 1:
        criteria["swissmetro"] = "The traveler chooses Swissmetro."

    if row["CAR_AV"] == 1:
        criteria["car"] = "The traveler chooses car."

    questions = {

        "mode_choice": {

            "type": "choice",

            "instructions": (
                "Predict which transportation mode this traveler will choose "
                "based on the traveler characteristics and the attributes of "
                "the available transportation alternatives."
            ),

            "criteria": criteria
        }
    }

    return questions

# ============================================================
# 4. 先测试第一行
# ============================================================

row = df.iloc[0]

state = row_to_state(row)

questions = row_to_questions(row)

print("\nState sent to JEV:")
print(state)

print("\nQuestion sent to JEV:")
print(questions)


result = ask_jev(
    state=state,
    questions=questions
)

print("\nJEV raw result:")
print(result)


# ============================================================
# 5. 读取 choice probability
# ============================================================

answer = result["answers"]["mode_choice"]

predicted_choice = answer["choice"]

probabilities = answer["probabilities"]

print("\nPredicted choice:")
print(predicted_choice)

print("\nChoice probabilities:")
print(probabilities)

print("\nObserved choice:")
print(row["CHOICE"])
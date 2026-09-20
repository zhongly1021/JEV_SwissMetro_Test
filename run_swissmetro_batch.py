import os
import time
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
    CHOICE_MAP,
    decode,
)


# ============================================================
# 路径
# ============================================================

INPUT_PATH = "data/raw/swissmetro.csv"
OUTPUT_PATH = "data/output/pred.csv"
os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)

BATCH_SIZE = 20


# ============================================================
# row -> JEV state
# ============================================================

def row_to_state(row):

    state = {
        "traveler": {
            #"population_group": decode(GROUP_MAP, row["GROUP"]),
            "survey_source": decode(SURVEY_MAP, row["SURVEY"]),
            #"survey_type": decode(SP_MAP, row["SP"]),
            #"respondent_id": int(row["ID"]),

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


# ============================================================
# availability -> choice criteria
# ============================================================

def row_to_criteria(row):

    criteria = {}

    if int(row["TRAIN_AV"]) == 1:
        criteria["train"] = (
            "The traveler chooses conventional train."
        )

    if int(row["SM_AV"]) == 1:
        criteria["swissmetro"] = (
            "The traveler chooses Swissmetro."
        )

    if int(row["CAR_AV"]) == 1:
        criteria["car"] = (
            "The traveler chooses car."
        )

    return criteria


# ============================================================
# 一个 batch 的预测
# ============================================================

def predict_batch(batch_df):

    records = []
    questions = {}

    for df_index, row in batch_df.iterrows():

        record_id = f"r{df_index}"

        # 每一行数据放入 records
        records.append({
            "id": record_id,
            "record": row_to_state(row)
        })

        # 每一行对应一个独立 choice question
        questions[f"{record_id}__mode_choice"] = {

            "type": "choice",

            "instructions": (
                f'For the record with id "{record_id}", '
                "predict which transportation mode the traveler "
                "would choose based on traveler characteristics, "
                "trip characteristics, and the attributes of the "
                "available transportation alternatives."
            ),

            "criteria": row_to_criteria(row)
        }

    state = {
        "description": (
            "Swissmetro stated-preference mode-choice observations. "
            "Each record represents one hypothetical travel choice situation."
        ),
        "records": records
    }

    result = ask_jev(
        state=state,
        questions=questions
    )

    return result["answers"]


# ============================================================
# 整个 dataset
# ============================================================

def main():

    df = pd.read_csv(INPUT_PATH)

    print(f"Loaded {len(df)} observations.")

    # 如果存在 CHOICE=0，则它没有 observed choice
    # 这里先排除
    df = df[df["CHOICE"] != 0].copy()

    # 保留原始 dataframe index，方便与 JEV record 对应
    df.reset_index(drop=True, inplace=True)

    if os.path.exists(OUTPUT_PATH):

        old_pred = pd.read_csv(OUTPUT_PATH)

        predictions = old_pred.to_dict(orient="records")

        completed_rows = set(
            old_pred["row_id"].astype(int)
        )
        print(
            f"Found checkpoint: "
            f"{len(completed_rows)} rows completed."
        )
    else:

        predictions = []
        completed_rows = set()

    total_batches = (
        len(df) + BATCH_SIZE - 1
    ) // BATCH_SIZE

    for batch_no, start in enumerate(
        range(0, len(df), BATCH_SIZE),
        start=1
    ):

        end = min(
            start + BATCH_SIZE,
            len(df)
        )

        batch_df = df.iloc[start:end]
        batch_df = batch_df[
            ~batch_df.index.isin(completed_rows)
        ]

        if batch_df.empty:
            print(f"Batch {batch_no} already completed, skip.")
            continue
        print(
            f"Batch {batch_no}/{total_batches}: "
            f"rows {start}-{end - 1}"
        )

        try:

            answers = predict_batch(batch_df)

            for df_index, row in batch_df.iterrows():

                record_id = f"r{df_index}"
                answer_key = f"{record_id}__mode_choice"

                answer = answers[answer_key]

                predicted_choice = answer["choice"]

                probabilities = answer["probabilities"]

                p_train = float(
                    probabilities.get("train", 0.0)
                )

                p_swissmetro = float(
                    probabilities.get("swissmetro", 0.0)
                )

                p_car = float(
                    probabilities.get("car", 0.0)
                )

                # confidence 定义为：
                # JEV 给 predicted choice 的 probability
                '''
                confidence = float(
                    probabilities[predicted_choice]
                )
                '''
                confidence = answer["confidence"]
                observed_code = int(row["CHOICE"])

                observed_choice = decode(
                    CHOICE_MAP,
                    observed_code
                )

                predictions.append({
                    "row_id": df_index,

                    "respondent_id": int(row["ID"]),

                    "p_train": p_train,
                    "p_swissmetro": p_swissmetro,
                    "p_car": p_car,

                    "predicted_choice": predicted_choice,
                    "confidence": confidence,

                    "observed_choice": observed_choice,
                    "observed_choice_code": observed_code,
                })

        except Exception as e:

            print(
                f"Error in batch {batch_no}: {e}"
            )

            # 当前 batch 失败时先终止，
            # 防止静默丢失 observation
            raise
        
        pd.DataFrame(predictions).to_csv(
            OUTPUT_PATH,
            index=False
        )

        print(
            f"Checkpoint saved: "
            f"{len(predictions)}/{len(df)}"
        )

        # 稍微避免请求过密
        time.sleep(0.1)

    # ========================================================
    # 保存结果
    # ========================================================

    pred_df = pd.DataFrame(predictions)

    os.makedirs(
        os.path.dirname(OUTPUT_PATH),
        exist_ok=True
    )

    pred_df.to_csv(
        OUTPUT_PATH,
        index=False
    )

    print()
    print("Finished.")
    print(f"Predictions saved to: {OUTPUT_PATH}")
    print()
    print(pred_df.head())


if __name__ == "__main__":
    main()
import pandas as pd
import numpy as np

from sklearn.metrics import (
    accuracy_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)


PRED_PATH = "data/output/pred.csv"


def normalize_choice(x):

    x = str(x).strip().lower()

    mapping = {
        "train": "train",
        "swissmetro": "swissmetro",
        "sm": "swissmetro",
        "car": "car",

        "1": "train",
        "2": "swissmetro",
        "3": "car",
    }

    return mapping.get(x, x)


def paper_divergence(p, q):
    """
    Divergence exactly following the equation shown in
    Liu et al. (2025).

    Note:
    The paper calls this Jensen-Shannon divergence,
    but mathematically this is symmetric KL divergence / 2.
    """

    eps = 1e-12

    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)

    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)

    return 0.5 * (
        np.sum(p * np.log(p / q))
        +
        np.sum(q * np.log(q / p))
    )


def standard_jsd(p, q):
    """
    Standard Jensen-Shannon divergence.
    """

    eps = 1e-12

    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)

    p = np.clip(p, eps, 1.0)
    q = np.clip(q, eps, 1.0)

    m = 0.5 * (p + q)

    return 0.5 * (
        np.sum(p * np.log(p / m))
        +
        np.sum(q * np.log(q / m))
    )


def main():

    df = pd.read_csv(PRED_PATH)

    print(f"Loaded {len(df)} predictions.")

    y_true = df["observed_choice"].apply(normalize_choice)
    y_pred = df["predicted_choice"].apply(normalize_choice)

    labels = [
        "train",
        "swissmetro",
        "car"
    ]

    # ============================================================
    # Accuracy
    # ============================================================

    accuracy = accuracy_score(
        y_true,
        y_pred
    )

    # ============================================================
    # Recall
    # ============================================================

    macro_recall = recall_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0
    )

    per_class_recall = recall_score(
        y_true,
        y_pred,
        labels=labels,
        average=None,
        zero_division=0
    )

    # ============================================================
    # F1
    # ============================================================

    macro_f1 = f1_score(
        y_true,
        y_pred,
        labels=labels,
        average="macro",
        zero_division=0
    )

    weighted_f1 = f1_score(
        y_true,
        y_pred,
        labels=labels,
        average="weighted",
        zero_division=0
    )

    per_class_f1 = f1_score(
        y_true,
        y_pred,
        labels=labels,
        average=None,
        zero_division=0
    )

    # ============================================================
    # Aggregate mode share
    # ============================================================

    observed_share = np.array([
        (y_true == label).mean()
        for label in labels
    ])

    predicted_share = np.array([
        (y_pred == label).mean()
        for label in labels
    ])

    # ============================================================
    # JSD / paper divergence
    # ============================================================

    paper_jsd = paper_divergence(
        observed_share,
        predicted_share
    )

    jsd = standard_jsd(
        observed_share,
        predicted_share
    )

    # ============================================================
    # Confusion matrix
    # ============================================================

    cm = confusion_matrix(
        y_true,
        y_pred,
        labels=labels
    )

    cm_df = pd.DataFrame(
        cm,
        index=[
            "Observed_Train",
            "Observed_Swissmetro",
            "Observed_Car"
        ],
        columns=[
            "Predicted_Train",
            "Predicted_Swissmetro",
            "Predicted_Car"
        ]
    )

    # ============================================================
    # Output
    # ============================================================

    print("\n========================================")
    print("Individual-level Prediction")
    print("========================================")

    print(f"Accuracy:       {accuracy:.4f}")
    print(f"Macro Recall:   {macro_recall:.4f}")
    print(f"Macro F1:       {macro_f1:.4f}")
    print(f"Weighted F1:    {weighted_f1:.4f}")

    print("\nPer-class performance:")

    for label, recall, f1 in zip(
        labels,
        per_class_recall,
        per_class_f1
    ):
        print(
            f"{label:12s} "
            f"Recall={recall:.4f} "
            f"F1={f1:.4f}"
        )

    print("\n========================================")
    print("Aggregate Mode Share")
    print("========================================")

    print(
        f"{'Mode':12s}"
        f"{'Observed':>12s}"
        f"{'Predicted':>12s}"
    )

    for label, obs, pred in zip(
        labels,
        observed_share,
        predicted_share
    ):
        print(
            f"{label:12s}"
            f"{obs:12.4f}"
            f"{pred:12.4f}"
        )

    print("\n========================================")
    print("Distribution Metrics")
    print("========================================")

    print(
        f"Paper divergence: {paper_jsd:.4f}"
    )

    print(
        f"Standard JSD:     {jsd:.4f}"
    )

    print("\n========================================")
    print("Confusion Matrix")
    print("========================================")

    print(cm_df)

    print("\n========================================")
    print("Classification Report")
    print("========================================")

    print(
        classification_report(
            y_true,
            y_pred,
            labels=labels,
            digits=4,
            zero_division=0
        )
    )


if __name__ == "__main__":
    main()
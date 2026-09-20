
# JEV for Swissmetro Mode Choice Prediction

This repository evaluates the zero-shot capability of **JEV** for individual-level transportation mode choice prediction using the **Swissmetro stated-preference dataset**.

The main idea is to transform each Swissmetro observation from coded tabular variables into a structured, human-readable decision state and send it to JEV through the OpenRouter Decisions API.

For each observation, JEV predicts the probability of choosing:

- Train
- Swissmetro
- Car

The predicted choice probabilities, JEV confidence score, and observed choice are then stored and evaluated at both the individual and aggregate levels.

---

## 1. Project Structure

```text
jev/
│
├── choice_jev.py
├── config.py
├── run_swissmetro_batch.py
├── evaluate.py
├── .env
│
├── data/
│   ├── raw/
│   │   └── swissmetro.csv
│   │
│   └── output/
│       └── pred.csv
│
└── README.md
```

The main files are:

| File | Description |
|---|---|
| `config.py` | Maps coded Swissmetro variables into human-readable descriptions |
| `choice_jev.py` | Sends structured decision requests to JEV through OpenRouter |
| `run_swissmetro_batch.py` | Reads the dataset, constructs prompts, performs batch prediction, and saves results |
| `evaluate.py` | Calculates accuracy, recall, F1, confusion matrix, mode shares, and distribution divergence |

---

## 2. Dataset

The experiment uses the Swissmetro stated-preference mode choice dataset.

Each observation represents a hypothetical transportation choice among three alternatives:

```text
1 = Train
2 = Swissmetro
3 = Car
```

The dataset contains traveler characteristics such as:

```text
PURPOSE
FIRST
TICKET
WHO
LUGGAGE
AGE
MALE
INCOME
GA
ORIGIN
DEST
```

and alternative-specific attributes such as:

```text
TRAIN_TT
TRAIN_CO
TRAIN_HE

SM_TT
SM_CO
SM_HE
SM_SEATS

CAR_TT
CAR_CO
```

The raw dataset is stored at:

```text
data/raw/swissmetro.csv
```

The observed variable `CHOICE` is **not provided to JEV**. It is used only as the ground-truth label during evaluation.

---

## 3. Variable Decoding

JEV is not given the original numerical category codes directly.

Instead, `config.py` converts the coded variables into human-readable descriptions.

For example:

```text
PURPOSE = 1
```

is converted to:

```text
Commuting
```

and:

```text
AGE = 3
```

is converted to:

```text
40 to 54 years old
```

Similarly:

```text
INCOME = 2
```

becomes:

```text
Annual income between CHF 50,000 and CHF 100,000
```

The Swissmetro `ORIGIN` and `DEST` variables correspond to Swiss cantons.

For example:

```text
ORIGIN = 2
DEST = 1
```

are converted to:

```text
Origin: Canton of Bern, Switzerland
Destination: Canton of Zürich, Switzerland
```

This preprocessing allows JEV to interpret the behavioral context without having to infer the meaning of dataset-specific numerical codes.

---

## 4. Prompt Construction

Each observation is converted into a structured decision state.

An example state is:

```python
{
    "traveler": {
        "population_group": "Population group 2",
        "survey_source": "Survey conducted on a train",
        "survey_type": "Stated-preference survey",
        "respondent_id": 1,
        "travel_purpose": "Commuting",
        "travel_class": "Not a first-class traveler",
        "ticket_type": "Round-trip ticket with half-fare card",
        "who_pays": "Traveler pays",
        "luggage": "No luggage",
        "age_group": "40 to 54 years old",
        "gender": "Female",
        "annual_income": "Annual income between CHF 50,000 and CHF 100,000",
        "ga_travelcard": "Does not own a Swiss GA annual travelcard"
    },

    "trip": {
        "origin": "Canton of Bern, Switzerland",
        "destination": "Canton of Zürich, Switzerland"
    },

    "alternatives": {
        "train": {
            "available": True,
            "travel_time_minutes": 112,
            "cost_chf": 48,
            "headway_minutes": 120
        },

        "swissmetro": {
            "available": True,
            "travel_time_minutes": 63,
            "cost_chf": 52,
            "headway_minutes": 20,
            "seat_configuration": "Standard Swissmetro seating"
        },

        "car": {
            "available": True,
            "travel_time_minutes": 117,
            "cost_chf": 65
        }
    }
}
```

The corresponding JEV decision question is:

```python
{
    "type": "choice",

    "instructions": (
        "Predict which transportation mode the traveler "
        "would choose based on traveler characteristics, "
        "trip characteristics, and the attributes of the "
        "available transportation alternatives."
    ),

    "criteria": {
        "train": "The traveler chooses conventional train.",
        "swissmetro": "The traveler chooses Swissmetro.",
        "car": "The traveler chooses car."
    }
}
```

If an alternative is unavailable, it is removed from the choice set before the request is sent to JEV.

---

## 5. JEV Prediction

The model is accessed through the OpenRouter Decisions API.

The current model is:

```text
typesafe/jev-1.13
```

The API key is stored in:

```text
.env
```

using:

```text
OPENROUTER_API_KEY=your_openrouter_api_key
```

Run the prediction script with:

```bash
python run_swissmetro_batch.py
```

The observations are processed in batches rather than sending the entire dataset in a single request.

The script also supports:

```text
automatic retry
checkpoint saving
resume from previous predictions
```

so temporary network or API interruptions do not require restarting the entire experiment.

---

## 6. JEV Output

For each observation, JEV returns a probability distribution over the available transportation alternatives.

A typical result is:

```text
predicted_choice = swissmetro

p_train       = 0.10
p_swissmetro  = 0.82
p_car         = 0.08

confidence    = 0.74
```

The probabilities represent JEV's decision distribution over the available alternatives.

The `confidence` value is directly returned by JEV. It is a statistic derived from the overall probability distribution and is not manually calculated as the maximum choice probability.

The final prediction file is stored at:

```text
data/output/pred.csv
```

with the following columns:

```text
row_id
respondent_id
p_train
p_swissmetro
p_car
predicted_choice
confidence
observed_choice
observed_choice_code
```

---

## 7. Evaluation

Run:

```bash
python evaluate.py
```

The evaluation includes:

```text
Accuracy
Macro Recall
Per-class Recall
Macro F1
Weighted F1
Per-class F1
Confusion Matrix
Observed Mode Share
Predicted Mode Share
Jensen-Shannon Divergence
```

The evaluation follows both individual-level prediction performance and aggregate behavioral distribution alignment.

---

# Results

A total of **10,719 observations** were successfully predicted.

## Individual-Level Prediction Performance

| Metric | Value |
|---|---:|
| Accuracy | **0.6221** |
| Macro Recall | **0.4115** |
| Macro F1 | **0.3996** |
| Weighted F1 | **0.5426** |

The class-specific performance is:

| Mode | Precision | Recall | F1-score | Support |
|---|---:|---:|---:|---:|
| Train | 0.5789 | 0.0773 | 0.1364 | 1,423 |
| Swissmetro | 0.6163 | 0.9546 | 0.7491 | 6,216 |
| Car | 0.6926 | 0.2026 | 0.3135 | 3,080 |

---

## Confusion Matrix

| Observed / Predicted | Train | Swissmetro | Car |
|---|---:|---:|---:|
| Train | 110 | 1,247 | 66 |
| Swissmetro | 71 | 5,934 | 211 |
| Car | 9 | 2,447 | 624 |

The confusion matrix shows a strong tendency to predict **Swissmetro**.

Among the 1,423 observed Train choices, only 110 are correctly identified.

Among the 3,080 observed Car choices, only 624 are correctly identified.

In contrast, 5,934 of the 6,216 observed Swissmetro choices are correctly predicted.

---

## Aggregate Mode Shares

The observed mode shares are:

| Mode | Observed Share |
|---|---:|
| Train | 13.28% |
| Swissmetro | 57.99% |
| Car | 28.73% |

The mode shares predicted by JEV are:

| Mode | Predicted Share |
|---|---:|
| Train | 1.77% |
| Swissmetro | 89.82% |
| Car | 8.41% |

A direct comparison is:

| Mode | Observed | JEV Predicted |
|---|---:|---:|
| Train | 13.28% | 1.77% |
| Swissmetro | 57.99% | 89.82% |
| Car | 28.73% | 8.41% |

The largest discrepancy is therefore the substantial over-prediction of Swissmetro.

---

## Distribution-Level Evaluation

The standard Jensen-Shannon divergence between the observed and predicted aggregate mode distributions is approximately:

```text
JSD = 0.0716
```

where:

\[
p =
(0.1328,\ 0.5799,\ 0.2873)
\]

is the observed mode distribution and:

\[
q =
(0.0177,\ 0.8982,\ 0.0841)
\]

is the predicted distribution.

The standard Jensen-Shannon divergence is calculated as:

\[
JSD(p,q)
=
\frac{1}{2} KL(p||m)
+
\frac{1}{2} KL(q||m)
\]

where:

\[
m=\frac{p+q}{2}.
\]

The evaluation code additionally implements the symmetric KL-style divergence equation reported in the referenced LLM-based mode-choice study:

**Large Language Models for Travel Choice Modeling**  
https://arxiv.org/abs/2505.19003

For the current JEV prediction results:

```text
Paper-style divergence ≈ 0.3104
```

The two metrics are reported separately because the equation used in the referenced paper is not mathematically identical to the standard Jensen-Shannon divergence.

---

# Result Analysis

The overall prediction accuracy of JEV is:

```text
62.21%
```

However, this value should not be interpreted independently of the class distribution.

Swissmetro accounts for approximately:

```text
57.99%
```

of all observed choices.

A naive classifier that predicts Swissmetro for every observation would therefore already obtain approximately:

```text
57.99% accuracy
```

JEV improves the overall accuracy by only about four percentage points over this majority-class baseline.

The more informative results are the class-specific recall and Macro F1.

JEV achieves:

```text
Train recall        = 0.0773
Swissmetro recall   = 0.9546
Car recall          = 0.2026
```

The model therefore successfully identifies most Swissmetro observations but fails to recover most Train and Car choices.

This imbalance is also reflected by:

```text
Macro Recall = 0.4115
Macro F1     = 0.3996
```

which are substantially lower than the overall accuracy.

At the aggregate level, the same behavior becomes more apparent.

The observed Swissmetro share is:

```text
57.99%
```

whereas JEV predicts:

```text
89.82%
```

of observations as Swissmetro.

At the same time, JEV predicts only:

```text
1.77% Train
8.41% Car
```

compared with the observed:

```text
13.28% Train
28.73% Car
```

The zero-shot JEV model therefore exhibits a strong **alternative-specific bias toward Swissmetro**.

---

## Interpretation

The current experiment should be interpreted as a **zero-shot behavioral prediction experiment**, rather than as an estimated discrete choice model.

Traditional discrete choice models estimate parameters using observed choices, for example:

\[
P(i|x)
=
\frac{\exp(V_i)}
{\sum_j \exp(V_j)}
\]

where the utility parameters are estimated by maximizing the likelihood of the observed dataset.

In the current experiment, JEV has not been trained or fine-tuned using the Swissmetro observations.

Instead, it directly generates:

\[
P_{\text{JEV}}
(
Train,
Swissmetro,
Car
\mid
Traveler,\ Trip,\ Alternatives
)
\]

using its pretrained decision model.

Therefore, the returned probabilities should currently be interpreted as **JEV decision probabilities**, rather than calibrated empirical choice probabilities for the Swissmetro population.

The results suggest that JEV is capable of extracting some individual-level behavioral information from structured travel attributes, but its zero-shot prior introduces a substantial systematic bias toward the novel Swissmetro alternative.

This bias is not fully visible from accuracy alone and becomes much clearer when examining:

```text
Macro F1
Per-class Recall
Confusion Matrix
Aggregate Mode Shares
Jensen-Shannon Divergence
```

These metrics are therefore important when evaluating LLM-based or JEV-based choice models.

---

# Current Pipeline

```text
Swissmetro Dataset
        │
        ▼
Read swissmetro.csv
        │
        ▼
Decode categorical variables
        │
        ▼
Construct human-readable traveler information
        │
        ▼
Construct trip information
        │
        ▼
Construct Train / Swissmetro / Car attributes
        │
        ▼
Build JEV structured decision state
        │
        ▼
OpenRouter Decisions API
        │
        ▼
JEV zero-shot prediction
        │
        ├── P(Train)
        ├── P(Swissmetro)
        ├── P(Car)
        ├── Predicted Choice
        └── Confidence
        │
        ▼
data/output/pred.csv
        │
        ▼
Individual-level evaluation
        │
        ├── Accuracy
        ├── Recall
        ├── Macro F1
        └── Weighted F1
        │
        ▼
Aggregate evaluation
        │
        ├── Mode Share
        └── Jensen-Shannon Divergence
```

---

# Current Findings

The main findings from the zero-shot experiment are:

```text
Accuracy        = 0.6221
Macro Recall    = 0.4115
Macro F1        = 0.3996
Weighted F1     = 0.5426

Observed Swissmetro Share  = 57.99%
Predicted Swissmetro Share = 89.82%
```

The results indicate that pretrained JEV can perform non-trivial mode-choice prediction without task-specific training, but its predictions are strongly biased toward Swissmetro.

This motivates subsequent experiments involving task-specific adaptation, including:

```text
Supervised Fine-Tuning
Choice Probability Calibration
RL-based Alignment
Comparison with MNL / Nested Logit
Comparison with general-purpose LLMs
```

The zero-shot JEV results in this repository serve as the baseline for these future experiments.

---

## Reference

Liu et al. (2025). *Large Language Models for Travel Choice Modeling.*

```text
https://arxiv.org/abs/2505.19003
```

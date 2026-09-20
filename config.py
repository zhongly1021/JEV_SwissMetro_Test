# config.py

# ============================================================
# Swissmetro variable mappings
# ============================================================

GROUP_MAP = {
    2: "Population group 2",
    3: "Population group 3",
}
# 原始文档只说 "Different groups in the population"
# 没有进一步说明 Group 2 / Group 3 的行为含义，因此不要自行解释。


SURVEY_MAP = {
    0: "Survey conducted on a train",
    1: "Survey conducted among car travelers",
}


SP_MAP = {
    1: "Stated-preference survey",
}


PURPOSE_MAP = {
    1: "Commuting",
    2: "Shopping",
    3: "Business",
    4: "Leisure",
    5: "Returning from work",
    6: "Returning from shopping",
    7: "Returning from business",
    8: "Returning from leisure",
    9: "Other purpose",
}


FIRST_MAP = {
    0: "Not a first-class traveler",
    1: "First-class traveler",
}


TICKET_MAP = {
    0: "No ticket",
    1: "Round-trip ticket with half-fare card",
    2: "One-way ticket with half-fare card",
    3: "Round-trip ticket at normal fare",
    4: "One-way ticket at normal fare",
    5: "Half-day ticket",
    6: "Annual season ticket",
    7: "Junior or senior annual season ticket",
    8: "Free travel after 7pm card",
    9: "Group ticket",
    10: "Other ticket type",
}


WHO_MAP = {
    0: "Payer unknown",
    1: "Traveler pays",
    2: "Employer pays",
    3: "Cost shared equally between traveler and employer",
}


LUGGAGE_MAP = {
    0: "No luggage",
    1: "One piece of luggage",
    3: "Several pieces of luggage",
}


AGE_MAP = {
    1: "24 years old or younger",
    2: "25 to 39 years old",
    3: "40 to 54 years old",
    4: "55 to 65 years old",
    5: "Older than 65 years",
    6: "Age unknown",
}


GENDER_MAP = {
    0: "Female",
    1: "Male",
}


INCOME_MAP = {
    0: "Annual income below CHF 50,000",
    1: "Annual income below CHF 50,000",
    2: "Annual income between CHF 50,000 and CHF 100,000",
    3: "Annual income above CHF 100,000",
    4: "Annual income unknown",
}


GA_MAP = {
    0: "Does not own a Swiss GA annual travelcard",
    1: "Owns a Swiss GA annual travelcard",
}


# ============================================================
# Canton mapping
#
# Swissmetro ORIGIN / DEST are canton codes, NOT city codes.
# ============================================================

CANTON_MAP = {
    1: "Canton of Zürich, Switzerland",
    2: "Canton of Bern, Switzerland",
    3: "Canton of Lucerne, Switzerland",
    4: "Canton of Uri, Switzerland",
    5: "Canton of Schwyz, Switzerland",
    6: "Canton of Obwalden, Switzerland",
    7: "Canton of Nidwalden, Switzerland",
    8: "Canton of Glarus, Switzerland",
    9: "Canton of Zug, Switzerland",
    10: "Canton of Fribourg, Switzerland",
    11: "Canton of Solothurn, Switzerland",
    12: "Canton of Basel-Stadt, Switzerland",
    13: "Canton of Basel-Landschaft, Switzerland",
    14: "Canton of Schaffhausen, Switzerland",
    15: "Canton of Appenzell Ausserrhoden, Switzerland",
    16: "Canton of Appenzell Innerrhoden, Switzerland",
    17: "Canton of St. Gallen, Switzerland",
    18: "Canton of Graubünden, Switzerland",
    19: "Canton of Aargau, Switzerland",
    20: "Canton of Thurgau, Switzerland",
    21: "Canton of Ticino, Switzerland",
    22: "Canton of Vaud, Switzerland",
    23: "Canton of Valais, Switzerland",
    24: "Canton of Neuchâtel, Switzerland",
    25: "Canton of Geneva, Switzerland",
    26: "Canton of Jura, Switzerland",
}


AVAILABILITY_MAP = {
    0: False,
    1: True,
}


SM_SEATS_MAP = {
    0: "Standard Swissmetro seating",
    1: "Airline-style seating",
}


CHOICE_MAP = {
    0: "Unknown",
    1: "Train",
    2: "Swissmetro",
    3: "Car",
}


# ============================================================
# Safe mapping function
# ============================================================

def decode(mapping, value):
    """
    Convert a coded Swissmetro value into a human-readable description.
    Falls back to the original value if an unexpected code occurs.
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        return str(value)

    return mapping.get(value, f"Unknown code ({value})")
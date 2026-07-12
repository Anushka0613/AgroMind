# Nutrient content of common fertilizers (percentage)
FERTILIZER_CONTENT = {
        "Urea (46-0-0)": {
            "nutrient": "N",
            "percentage": 46
        },
        "DAP - Di-Ammonium Phosphate (18-46-0)": {
            "nutrient": "P",
            "percentage": 46
        },
        "MOP - Muriate of Potash (0-0-60)": {
            "nutrient": "K",
            "percentage": 60
        },
        "Balanced NPK (e.g. 19-19-19)": {
            "nutrient": "NPK",
            "percentage": 19
        }
    }
def calculate_dosage(
    fertilizer_name,
    nutrient_gap,
    farm_size,
    unit="acre"
):
    """
    Calculates the amount of fertilizer required based on the
    nutrient deficiency, fertilizer nutrient percentage,
    and farm size.

    Parameters:
        fertilizer_name (str): Name of the fertilizer.
        nutrient_gap (float): Required nutrient amount (kg/ha).
        farm_size (float): Size of the farm.
        unit (str): 'acre' or 'hectare'.

    Returns:
        dict: Fertilizer dosage recommendation.
    """
    # Check if the fertilizer is supported
    if fertilizer_name not in FERTILIZER_CONTENT:
        raise ValueError(f"Unsupported fertilizer: {fertilizer_name}")
    
    fertilizer = FERTILIZER_CONTENT[fertilizer_name]
    nutrient_percentage = fertilizer["percentage"]

     # Farm size must be greater than zero
    if farm_size <= 0:
        raise ValueError("Farm size must be greater than zero.")
    
    # Convert acres to hectares if required
    if unit.lower() == "acre":
        area = farm_size * 0.4047
    elif unit.lower() == "hectare":
        area = farm_size
    else:
        raise ValueError("Unit must be either 'acre' or 'hectare'.")
    
    # Calculate fertilizer required per hectare
    dosage_per_hectare = (nutrient_gap * 100) / nutrient_percentage

    # Calculate total fertilizer required for the given farm size
    total_required = dosage_per_hectare * area

    return {
        "fertilizer": fertilizer_name,
        "dosage_per_hectare": round(dosage_per_hectare, 2),
        "farm_size": farm_size,
        "unit": unit,
        "total_required": round(total_required, 2)
    }
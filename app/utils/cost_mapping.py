# Cost mapping based on Damage Type and Severity

COST_MAPPING = {
    "no_damage": {
        "minor": "$0",
        "moderate": "$0",
        "severe": "$0"
    },
    "scratch": {
        "minor": "$100 - $300",
        "moderate": "$300 - $800",
        "severe": "$800 - $1,500"
    },
    "dent": {
        "minor": "$200 - $500",
        "moderate": "$500 - $1,200",
        "severe": "$1,200 - $3,000"
    },
    "broken_glass": {
        "minor": "$150 - $400",
        "moderate": "$400 - $800",
        "severe": "$800 - $1,500"
    },
    "broken_lamp": {
        "minor": "$100 - $300",
        "moderate": "$300 - $800",
        "severe": "$800 - $1,200"
    },
    "crushed_panel": {
        "minor": "$1,000 - $2,500",
        "moderate": "$2,500 - $5,000",
        "severe": "$5,000+"
    }
}

def estimate_cost(damage_type, severity):
    return COST_MAPPING.get(damage_type, {}).get(severity, "Unknown")

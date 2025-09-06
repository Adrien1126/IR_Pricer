from enum import Enum, auto

class PricerType(Enum):
    """Types de pricers supportés."""
    DISCOUNTING = auto()  # Pricing par actualisation
    # Ajoute d'autres types ici plus tard (ex: MONTE_CARLO)

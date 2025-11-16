import enum


class Percentile(enum.Enum):
    """
    Enumeration of key percentile thresholds for fetal biometric evaluation.
    These correspond to percentile cutoffs used in standard reference tables
    such as NIHCD and INTERGROWTH-21st.

    Values are named rather than numeric for semantic clarity and future
    extension to customized percentile configurations.
    """

    Third = "Third percentile"
    Fifth = "Fifth percentile"
    Tenth = "Tenth percentile"
    Fiftieth = "Fiftieth percentile"
    Ninetieth = "Ninetieth percentile"
    Ninetyfifth = "Ninetyfifth percentile"
    Ninetyseventh = "Ninetyseventh percentile"

    @property
    def value_numeric(self) -> int:
        """Return the numeric percentile value (3,5,10,50,90,95,97)."""
        match self:
            case Percentile.Third: return 3
            case Percentile.Fifth: return 5
            case Percentile.Tenth: return 10
            case Percentile.Fiftieth: return 50
            case Percentile.Ninetieth: return 90
            case Percentile.Ninetyfifth: return 95
            case Percentile.Ninetyseventh: return 97
        raise ValueError(f"No numeric mapping for {self}")
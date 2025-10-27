from enum import Enum


class PercentileRange(Enum):
    BELOW_3P = "below_3p"
    BETWEEN_3P_5P = "between_3p_5p"
    BETWEEN_5P_10P = "between_5p_10p"
    BETWEEN_10P_50P = "between_10p_50p"
    BETWEEN_50P_90P = "between_50p_90p"
    BETWEEN_90P_95P = "between_90p_95p"
    BETWEEN_95P_97P = "between_95p_97p"
    ABOVE_97P = "above_97p"

    @classmethod
    def from_string(cls, s: str) -> "PercentileRange":
        """Return the enum corresponding to the given string label."""
        normalized = s.strip().lower()
        for member in cls:
            if member.value == normalized:
                return member
        raise ValueError(f"Unknown percentile range string: {s}")

    def to_string(self) -> str:
        """Return the string label for this percentile range."""
        return self.value

    def __str__(self):
        return self.value
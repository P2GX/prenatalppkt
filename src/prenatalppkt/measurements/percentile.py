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





percentile_to_result = {
 Percentile.Third: "low",
  Percentile.Fifth: "normal",
   Percentile.Tenth: "low",
    Percentile.Third: "low",
     Percentile.Third: "low",
      Percentile.Third: "low",
       Percentile.Third: "low",


}
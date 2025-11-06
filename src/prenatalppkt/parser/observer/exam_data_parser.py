import logging
import typing
from prenatalppkt.dto.exam_data import ExamData

logger = logging.getLogger(__name__)


class ExamDataParser:
   """
   Parser for extracting ExamData from Observer JSON
   """

   def parse(self, json_data: typing.Dict[str, object]) -> ExamData:
       """
       Parse raw JSON into an ExamData instance
       """
       if not isinstance(json_data, dict):
           raise ValueError(
               f"malformed arguement, expecting `dict` but got {type(json_data)}"
           )

       if "patient" not in json_data:
           raise ValueError("did not find 'patient' in exam")

       patient = json_data.get("patient")

       first_name = patient.get("first_name", "NA")
       last_name = patient.get("last_name", "NA")

       # TODO(@VarenyaJ): Find a secure way to create a patient identifier when used with Terra.
       individual_id = f"{first_name}_{last_name}"

       if "pt_age_at_exam" not in json_data:
           raise ValueError(
               f"Expecting patient age in 'pt_age_at_exam'; found keys={list(json_data.keys())}"
           )
       pt_age_at_exam = json_data.get("pt_age_at_exam")
       logger.debug("Parsed pt_age_at_exam=%s", pt_age_at_exam)

       return ExamData(mother_id=individual_id, maternal_age_at_exam=pt_age_at_exam)
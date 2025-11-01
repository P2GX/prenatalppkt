import typing
import logging
from prenatalppkt.dto.exam_data import ExamData


class ExamDataParser:
    def parse (self, json_data: typing.Dict[str, object]) -> ExamData:
        if not isinstance(json_data, dict):
            raise ValueError(f"malformed arguement, expecting `dict` but got {type(json_data)}")
    
        if "patient" not in json_data:
            raise ValueError(f"did not find 'patient' in exam")

        patient = json_data.get("patient")

        first_name = patient.get('first_name', "NA")
        last_name = patient.get('last_name', "NA")

        # TODO: @VarenyaJ please find a secure way to create a patient identifier when in use with Terra
        individual_id = f"{first_name}_{last_name}"

        if "pt_age_at_exam" not in json_data:
            msg = f"Did not find 'pt_age_at_exam'; found {'-'.join(json_data.keys())}"
            raise ValueError(f"expecting patient age in 'pt_age_at_exam'")
        pt_age_at_exam = json_data.get("pt_age_at_exam")
        print(pt_age_at_exam)

        return ExamData(mother_id=individual_id, maternal_age_at_exam=pt_age_at_exam)
import typing

class FetusData:
    #_mother_id: str
    #_maternal_age_at_exam: str
    _hpo_term_list: typing.List[SimpleTerm]

    def __init__(self, hpo_term_list) -> None:
        #self._mother_id = mother_id
        #self._maternal_age_at_exam = maternal_age_at_exam
        self._hpo_term_list = hpo_term_list
    
    @property
    def hpo_term_list(self):
        return self._hpo_term_list

    #@property
    #def mother_id(self):
    #    return self._mother_id

    #@property
    #def maternal_age_at_exam(self):
    #    return self._maternal_age_at_exam

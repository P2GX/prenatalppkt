import typing
from prenatalppkt.parser.viewpoint.sections.viewpoint_pregnancy_parse import (
    ViewpointPregnancyParser,
)


## Expect three lines of input with first and third being one space
def create_input(line: str) -> typing.List[str]:
    return [" ", line, " "]


class TestViewpointPregnancyParser:
    def __init__(self, lines: typing.List[str]):
        pass


def test_pregnancy_1():
    input = create_input("Singleton pregnancy. Number of fetuses: 1")
    parser = ViewpointPregnancyParser(lines=input)
    n_preg = parser.n_pregnancies()
    assert 1 == n_preg


def test_pregnancy_2():
    input = create_input("Twin pregnancy. Number of fetuses: 2")
    parser = ViewpointPregnancyParser(lines=input)
    n_preg = parser.n_pregnancies()
    assert 2 == n_preg

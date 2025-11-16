#

import typing
from pathlib import Path
from collections import defaultdict

from prenatalppkt.parser.viewpoint.viewpoint_text_sections import SectionHeader


class ViewpointTextParse:
    """
    Constructor for the text parser for ViewPoint6 files
    """

    def __init__(self, input: typing.Union[typing.List[str], Path]):
        if isinstance(input, Path):
            lines = input.read_text().splitlines()
        elif isinstance(input, typing.List[str]):
            lines = input
        else:
            raise ValueError(f"Input was not list or path, but was: {type(input)}")

        self._section_d = self._get_sections(lines)

    def is_divider(line: str) -> bool:
        """
        Function to get the divider strings i.e. ("===")

        Args:
            line (str): _description_

        Returns:
            bool: _description_
        """
        for c in line:
            if c != "=":
                return False
        return len(line) >= 3

    # TODO: @VarenyaJ, check if the section headers are always succeeded by at least three equal signs and then a newline

    def _get_sections(
        self, lines: typing.List[str]
    ) -> typing.Dict[SectionHeader, typing.List[str]]:
        """
        Function to get the starts and ends of sections within the text export of a ViewPoint6 report

        Args:
            lines (typing.List[str]): _description_

        Returns:
            typing.Dict[str, typing.List[str]]: _description_
        """
        indx = [
            i for i, line in enumerate(lines) if ViewpointTextParse.is_divider(line)
        ]
        # for i in indx: print(i)
        block_start_idx = [i - 1 for i in indx]
        print(block_start_idx)
        block_end_idx = [i for i in block_start_idx[1:]]
        block_end_idx.append(len(lines))
        print(block_end_idx)
        section_d = defaultdict(list)
        for i in range(len(block_start_idx)):
            s = block_start_idx[i]
            e = block_end_idx[i]
            section = lines[s + 2 : e]
            title = SectionHeader.from_string(lines[s].strip())
            section_d[title] = section
        return section_d

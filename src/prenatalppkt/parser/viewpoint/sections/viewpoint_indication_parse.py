import typing
import logging
from prenatalppkt.parser.viewpoint.viewpoint_text_sections import SectionHeader

logger = logging.getLogger(__name__)


class ViewpointIndicationParser:
    """
    Parse the Indication section from ViewPoint text export.

    The Indication section typically contains single or multiple lines
    describing the reason for the ultrasound examination, such as:
    - "Known or suspected fetal anomaly. Interval fetal growth"
    - "Fetal Growth Restriction. Growth/Doppler"
    - "Known fetal cardiac abnormality"

    The parser extracts indication text and splits it into individual
    indication items (sentences or bullet points).
    """

    def __init__(self, lines: typing.List[str]):
        """
        Initialize the parser with lines from the Indication section.

        Parameters
        ----------
        lines : typing.List[str]
            Lines from the ViewPoint text export, expected to contain
            the Indication section content (not including the header).

        Raises
        ------
        ValueError
            If no valid indication text is found in the input lines.
        """
        self._indication_items = self._parse_indication(lines)
        self._indication_text = " ".join(self._indication_items)

        logger.debug("Parsed indication items: %s", self._indication_items)

        if not self._indication_text:
            raise ValueError("No valid indication text found in input lines")

    def _parse_indication(self, lines: typing.List[str]) -> typing.List[str]:
        """
        Extract and parse indication text from the input lines.

        Parameters
        ----------
        lines : typing.List[str]
            Raw text lines from the Indication section.

        Returns
        -------
        typing.List[str]
            List of parsed indication items (sentences/bullet points).
        """
        # Get all section header values from the enum
        section_header_values = {member.value for member in SectionHeader}

        # Filter out empty lines, section headers, and divider lines using list comprehension
        filtered_lines = [
            line.strip()
            for line in lines
            if line.strip()
            and not self._is_divider(line)
            and line.strip() not in section_header_values
        ]

        if not filtered_lines:
            return []

        # Join all lines into a single text block
        text = " ".join(filtered_lines)

        logger.debug("Combined indication text: %s", text)

        # Split into sentences based on sentence-ending punctuation
        # Keep bullet points (lines starting with dash) as separate items
        indication_items = self._split_into_items(text)

        return indication_items

    def _is_divider(self, line: str) -> bool:
        """
        Check if a line is a section divider (e.g., "========").

        Parameters
        ----------
        line : str
            Line to check.

        Returns
        -------
        bool
            True if the line is a divider.
        """
        stripped = line.strip()
        return len(stripped) >= 3 and all(c == "=" for c in stripped)

    def _split_into_items(self, text: str) -> typing.List[str]:
        """
        Split text into individual indication items.

        Handles:
        - Sentences ending with . ! ?
        - Bullet points marked with dashes

        Parameters
        ----------
        text : str
            Combined indication text.

        Returns
        -------
        typing.List[str]
            List of individual indication items.
        """
        # For simple cases (most common), just split on '. '
        # This preserves the text structure while separating distinct indications
        items = []
        current = []

        words = text.split()
        for word in words:
            current.append(word)
            # Check if this word ends a sentence
            if word.endswith((".", "!", "?")):
                items.append(" ".join(current))
                current = []

        # Add any remaining text
        if current:
            items.append(" ".join(current))

        # Filter out any empty items
        items = [item.strip() for item in items if item.strip()]

        logger.debug("Split indication into %d items", len(items))

        return items if items else [text]  # Return original text if splitting fails

    @property
    def indication(self) -> str:
        """
        Get the complete parsed indication text as a single string.

        Returns
        -------
        str
            The complete indication text describing the reason for the exam.
        """
        return self._indication_text

    @property
    def indication_items(self) -> typing.List[str]:
        """
        Get the parsed indication as a list of individual items.

        Returns
        -------
        typing.List[str]
            List of indication items (sentences/bullet points).
        """
        return self._indication_items

    def __repr__(self) -> str:
        """String representation of the parser."""
        return f"ViewpointIndicationParser(items={len(self._indication_items)}, indication='{self.indication}')"

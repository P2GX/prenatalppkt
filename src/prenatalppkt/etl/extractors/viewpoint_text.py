"""
ViewPoint text file biometry extractor.

Extracts fetal biometry measurements from ViewPoint ultrasound system text exports.
Uses divider-based section detection (like ViewpointTextParse) to handle sub-headers.
"""

import logging
import re
from pathlib import Path
from typing import List, Optional

from prenatalppkt.etl.extractors.base import BiometryExtractor
from prenatalppkt.etl.models.biometry import Biometry, BiometryCollection
from prenatalppkt.etl.constants import (
    VIEWPOINT_TEXT_NAME_MAP,
    BiometryMeasurement,
    SectionHeader,
)

logger = logging.getLogger(__name__)


class ViewPointTextExtractor(BiometryExtractor):
    """
    Extract biometry measurements from ViewPoint text format.

    ViewPoint text structure:
        Fetal Biometry
        ============

        BPD          63.2          mm          25w 4d          36%          Hadlock
        OFD          82.9          mm          25w 0d          37%          Nicolaides
        HC           233.7         mm          25w 1d          36%          Chervenak
        AC           221.0         mm          26w 4d          67%          Hadlock
        Femur        48.5          mm          26w 2d          54%          Hadlock

        Head / Face / Neck Biometry:
        Nuchal Fold  4.5           mm          25w 2d          10%          Standard
        Cerebellum   30.0          mm          25w 3d          40%          Standard

    Uses divider-based section detection (====) to naturally handle sub-headers.
    Each line is space-delimited with fields:
    [name] [value] [unit] [GA_weeks] [GA_days] [percentile] [method]
    """

    # Use ViewPoint text-specific name mapping
    FORMAT_NAME_MAP = VIEWPOINT_TEXT_NAME_MAP

    # Section header for biometry data
    BIOMETRY_HEADER = SectionHeader.FETAL_BIOMETRY.value

    # Target measurements (canonical names)
    TARGET_MEASUREMENTS = BiometryMeasurement.all_values()

    def extract(self, data: str) -> BiometryCollection:
        """
        Extract biometry measurements from ViewPoint text.

        Args:
            data: ViewPoint text file content as string

        Returns:
            BiometryCollection with extracted measurements

        Raises:
            ValueError: If text format is invalid
        """
        if not isinstance(data, str):
            raise ValueError(f"Expected string, got {type(data)}")

        lines = data.split("\n")
        biometry_lines = self._find_biometry_section(lines)

        if not biometry_lines:
            logger.warning("No 'Fetal Biometry' section found")
            return BiometryCollection(measurements=[], fetus_number=None)

        measurements = self._parse_biometry_lines(biometry_lines)

        logger.info(f"Extracted {len(measurements)} biometries from ViewPoint text")

        return BiometryCollection(
            measurements=measurements,
            fetus_number=None,  # ViewPoint text doesn't specify fetus number
        )

    def _read_file(self, filepath: Path) -> str:
        """Read ViewPoint text file."""
        with open(filepath, "r", encoding="utf-8") as f:
            return f.read()

    def _is_divider(self, line: str) -> bool:
        """
        Check if a line is a section divider (====).

        Args:
            line: Line to check

        Returns:
            True if the line is a divider (3+ consecutive '=' characters)
        """
        stripped = line.strip()
        return len(stripped) >= 3 and all(c == "=" for c in stripped)

    def _find_biometry_section(self, lines: List[str]) -> List[str]:
        """
        Find lines in the Fetal Biometry section using divider-based detection.

        Uses the same approach as ViewpointTextParse from the old parser:
        - Sections are delimited by ==== lines
        - Section header is the line BEFORE the ====
        - Content is all lines until the NEXT ==== line

        This naturally handles sub-headers like "Head / Face / Neck Biometry:"

        Args:
            lines: All lines from the text file

        Returns:
            List of lines in the biometry section (until next section or empty line)
        """
        # Find all divider line indices
        divider_indices = [i for i, line in enumerate(lines) if self._is_divider(line)]

        if not divider_indices:
            logger.debug("No divider lines found in ViewPoint text")
            return []

        # Find the Fetal Biometry section
        biometry_start_idx = None
        biometry_end_idx = None

        for i, divider_idx in enumerate(divider_indices):
            # Check if line before divider is our header
            if divider_idx > 0:
                header = lines[divider_idx - 1].strip()
                if header == self.BIOMETRY_HEADER:
                    # Found it! Start after the divider
                    biometry_start_idx = divider_idx + 1
                    # End at next divider (or end of file)
                    if i + 1 < len(divider_indices):
                        biometry_end_idx = divider_indices[i + 1] - 1
                    else:
                        biometry_end_idx = len(lines)
                    break

        if biometry_start_idx is None:
            logger.debug(f"'{self.BIOMETRY_HEADER}' section not found")
            return []

        # Extract all non-empty, non-divider lines in this section
        section_lines = []
        for line in lines[biometry_start_idx:biometry_end_idx]:
            stripped = line.strip()
            if stripped and not self._is_divider(stripped):
                # Include all lines - parser will filter out sub-headers naturally
                section_lines.append(stripped)

        logger.debug(f"Found {len(section_lines)} lines in biometry section")
        return section_lines

    def _parse_biometry_lines(self, lines: List[str]) -> List[Biometry]:
        """
        Parse biometry measurement lines.

        Args:
            lines: Lines from biometry section

        Returns:
            List of Biometry objects
        """
        biometries = []

        for line in lines:
            try:
                biometry = self._parse_biometry_line(line)
                if biometry:
                    biometries.append(biometry)
            except Exception as e:
                logger.warning(f"Failed to parse biometry line '{line}': {e}")

        return biometries

    def _parse_biometry_line(self, line: str) -> Optional[Biometry]:
        """
        Parse a single biometry line.

        Format: [name] [value] [unit] [GA_weeks] [GA_days] [percentile] [method]
        Example: "BPD    63.2    mm    25w 4d    36%    Hadlock"
        Example: "Nuchal Fold    4.5    mm    25w 3d    10%    Standard"

        Sub-header lines like "Head / Face / Neck Biometry:" will naturally
        fail parsing (not enough parts) and be skipped.

        Args:
            line: Single line from biometry section

        Returns:
            Biometry object or None if parsing fails or not a target measurement
        """
        # Split by whitespace (handles variable spacing)
        parts = line.split()

        # Need at least 6 parts for a valid measurement line
        # Sub-headers and other lines won't have this many parts
        if len(parts) < 6:
            logger.debug(f"Line has fewer than 6 parts, skipping: {line}")
            return None

        # Try multi-word name first (e.g., "Nuchal Fold")
        # Check if combining first two parts creates a valid measurement
        name = None
        value_idx = None

        if len(parts) >= 7:  # Need extra part for two-word names
            two_word_name = f"{parts[0]} {parts[1]}"
            if self._is_target_measurement(two_word_name):
                name = two_word_name
                value_idx = 2  # Value starts at index 2 for two-word names

        # Fall back to single-word name
        if name is None:
            single_word_name = parts[0]
            if self._is_target_measurement(single_word_name):
                name = single_word_name
                value_idx = 1  # Value starts at index 1 for single-word names
            else:
                logger.debug(
                    f"'{single_word_name}' is not a target measurement, skipping"
                )
                return None

        # Normalize the name
        normalized_name = self._normalize_name(name)

        try:
            value = float(parts[value_idx])
            unit = parts[value_idx + 1]

            # Convert to mm if needed
            value_mm = self._convert_to_mm(value, unit)

            # Parse gestational age (format: "25w" "4d" or "25w" or just weeks)
            ga_weeks_str = parts[value_idx + 2] if len(parts) > value_idx + 2 else None
            ga_days_str = parts[value_idx + 3] if len(parts) > value_idx + 3 else None

            gestational_age = None
            if ga_weeks_str:
                # Handle combined format like "25w4d" or separate "25w" "4d"
                if "w" in ga_weeks_str:
                    weeks = ga_weeks_str.replace("w", "").strip()
                    if ga_days_str and "d" in ga_days_str:
                        days = ga_days_str.replace("d", "").strip()
                        gestational_age = f"G{weeks}w{days}d"
                    else:
                        gestational_age = f"G{weeks}w0d"

            # Parse percentile (format: "36%" or "<1%" or ">99%")
            percentile_str = (
                parts[value_idx + 4]
                if len(parts) > value_idx + 4 and "%" in parts[value_idx + 4]
                else None
            )
            percentile = (
                self._parse_percentile(percentile_str) if percentile_str else None
            )

            # Extract method (everything after percentile)
            method = parts[value_idx + 5] if len(parts) > value_idx + 5 else None

            return Biometry(
                name=normalized_name,
                value_mm=value_mm,
                percentile=percentile,
                gestational_age=gestational_age,
                method=method,
                fetus_number=None,  # ViewPoint text doesn't specify fetus number
            )

        except (ValueError, IndexError) as e:
            logger.debug(f"Failed to parse numeric values from line '{line}': {e}")
            return None

    def _format_ga(self, weeks_str: str, days_str: str) -> str:
        """
        Format gestational age from separate weeks and days strings.

        Args:
            weeks_str: Weeks string (e.g., "25w")
            days_str: Days string (e.g., "4d")

        Returns:
            Formatted GA string (e.g., "G25w4d")
        """
        # Extract numbers
        weeks = re.search(r"(\d+)", weeks_str)
        days = re.search(r"(\d+)", days_str)

        if not weeks or not days:
            return f"{weeks_str}{days_str}"  # Fallback

        return f"G{weeks.group(1)}w{days.group(1)}d"

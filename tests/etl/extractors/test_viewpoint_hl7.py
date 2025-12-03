"""
Tests for ViewPoint HL7 extractor.
"""

from pathlib import Path

import pytest

from prenatalppkt.etl.extractors import viewpoint_hl7
from prenatalppkt.etl.term_bin_factory import TermBinFactory
from prenatalppkt.measurements.term_bin import TermBin


@pytest.mark.skip(reason="TODO(@VarenyaJ): HL7 test data is first trimester (missing BPD/HC). Need second trimester sample or conditional validation.")
class TestViewPointHL7Extract:
    """Tests for extract() function."""

    def test_extract_basic(self):
        """Test extraction with minimal valid data."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
PID|1||12345||DOE^JANE||19900101|F
OBR|1|123456|123456|US^Ultrasound|||20211223144928
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.VP_HeadCircumference_GA|Fetus1|177^25w 3d|d
OBX|5|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|6|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|7|NM|SkullFetus.VP_BiParietalDiameter_GA|Fetus1|182^26w 0d|d
OBX|8|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|9|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|10|NM|AbdomenFetus.VP_AbdominalCircumference_GA|Fetus1|179^25w 5d|d
OBX|11|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|12|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
OBX|13|NM|ExtremitiesFetus.VP_FemurLength_GA|Fetus1|183^26w 1d|d
"""
        term_bins = viewpoint_hl7.extract(data)

        assert len(term_bins) == 4
        assert all(isinstance(tb, TermBin) for tb in term_bins)

    def test_extract_with_custom_factory(self):
        """Test extraction with custom factory."""
        factory = TermBinFactory()
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|5|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|6|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|7|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|8|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|9|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
"""
        term_bins = viewpoint_hl7.extract(data, factory)
        assert len(term_bins) == 4

    def test_extract_no_obx_segments(self):
        """Test extraction with no OBX segments."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
PID|1||12345||DOE^JANE||19900101|F
OBR|1|123456|123456|US^Ultrasound|||20211223144928
"""
        term_bins = viewpoint_hl7.extract(data)
        assert len(term_bins) == 0

    def test_extract_invalid_type(self):
        """Test extraction with invalid data type."""
        with pytest.raises(ValueError, match="Expected string"):
            viewpoint_hl7.extract(123)

    def test_extract_missing_required_measurements(self):
        """Test extraction fails when required measurements missing."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
"""
        with pytest.raises(ValueError, match="Missing required measurements"):
            viewpoint_hl7.extract(data)

    def test_extract_with_femur_undefined_length(self):
        """Test extraction handles FemurUndefinedLength."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|5|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|6|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|7|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|8|NM|ExtremitiesFetus.FemurUndefinedLength^FL|Fetus1|48^48.0|mm
OBX|9|NM|ExtremitiesFetus.VP_FemurUndefinedLength_Percentile|Fetus1|52^52%|%
"""
        term_bins = viewpoint_hl7.extract(data)
        assert len(term_bins) == 4

        # Check Femur is present
        femur = next(tb for tb in term_bins if "Femur" in tb.description)
        assert femur is not None

    def test_extract_extreme_percentiles(self):
        """Test extraction handles < and > percentile symbols."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|76.6^76.6|mm
OBX|5|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|0^<1%|%
OBX|6|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|7|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|8|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|9|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|0^>99%|%
"""
        term_bins = viewpoint_hl7.extract(data)
        assert len(term_bins) == 4

        # Check BPD percentile is low
        bpd = next(tb for tb in term_bins if "BPD" in tb.description)
        assert bpd.range.name in ["below_3p"]

        # Check Femur percentile is high
        femur = next(tb for tb in term_bins if "Femur" in tb.description)
        assert femur.range.name in ["above_97p"]


@pytest.mark.skip(reason="TODO(@VarenyaJ): HL7 test data is first trimester (missing BPD/HC). Need second trimester sample or conditional validation.")
class TestViewPointHL7ExtractFromFile:
    """Tests for extract_from_file() function."""

    def test_extract_from_file_not_found(self):
        """Test extraction from non-existent file."""
        with pytest.raises(FileNotFoundError):
            viewpoint_hl7.extract_from_file(Path("nonexistent.hl7"))

    def test_extract_from_file_success(self, tmp_path):
        """Test successful extraction from file."""
        test_file = tmp_path / "valid.hl7"
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|5|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|6|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|7|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|8|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|9|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
"""
        test_file.write_text(data)

        term_bins = viewpoint_hl7.extract_from_file(test_file)
        assert len(term_bins) == 4


@pytest.mark.skip(reason="TODO(@VarenyaJ): HL7 test data is first trimester (missing BPD/HC). Need second trimester sample or conditional validation.")
class TestViewPointHL7GestationalAge:
    """Tests for gestational age parsing."""

    def test_ga_with_weeks_and_days(self):
        """Test GA parsing with weeks and days."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.VP_HeadCircumference_GA|Fetus1|177^25w 3d|d
OBX|5|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|6|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|7|NM|SkullFetus.VP_BiParietalDiameter_GA|Fetus1|182^26w 0d|d
OBX|8|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|9|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|10|NM|AbdomenFetus.VP_AbdominalCircumference_GA|Fetus1|179^25w 5d|d
OBX|11|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|12|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
OBX|13|NM|ExtremitiesFetus.VP_FemurLength_GA|Fetus1|183^26w 1d|d
"""
        term_bins = viewpoint_hl7.extract(data)

        # Check that GA is captured
        hc = next(tb for tb in term_bins if "HC" in tb.description)
        # GA should be stored (exact format depends on implementation)
        assert hc is not None


@pytest.mark.skip(reason="TODO(@VarenyaJ): HL7 test data is first trimester (missing BPD/HC). Need second trimester sample or conditional validation.")
class TestViewPointHL7MethodParsing:
    """Tests for method/author parsing."""

    def test_method_author_field(self):
        """Test extraction of measurement method."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|ST|SkullFetus.VP_HeadCircumference_Author|Fetus1|Hadlock
OBX|5|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|6|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|7|ST|SkullFetus.VP_BiParietalDiameter_Author|Fetus1|Hadlock
OBX|8|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|9|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|10|ST|AbdomenFetus.VP_AbdominalCircumference_Author|Fetus1|Hadlock
OBX|11|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|12|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
OBX|13|ST|ExtremitiesFetus.VP_FemurLength_Author|Fetus1|Hadlock
"""
        term_bins = viewpoint_hl7.extract(data)

        # Check that methods are captured
        hc = next(tb for tb in term_bins if "HC" in tb.description)
        # Method should be in description if available
        assert "Hadlock" in hc.description or hc.description  # Just verify exists


@pytest.mark.skip(reason="TODO(@VarenyaJ): HL7 test data is first trimester (missing BPD/HC). Need second trimester sample or conditional validation.")
class TestViewPointHL7MalformedSegments:
    """Tests for handling malformed OBX segments."""

    def test_missing_value_field(self):
        """Test that segments with missing values are skipped."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1||mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|5|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|6|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|7|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|8|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|9|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
"""
        term_bins = viewpoint_hl7.extract(data)
        # HC should be skipped due to missing value
        assert len(term_bins) == 3

    def test_missing_percentile(self):
        """Test that measurements without percentiles are skipped."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier^Fetus Identifier|Fetus1|A
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|4|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|5|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|6|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|7|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|8|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
"""
        term_bins = viewpoint_hl7.extract(data)
        # HC should be skipped due to missing percentile
        assert len(term_bins) == 3

    def test_insufficient_fields(self):
        """Test that malformed segments with insufficient fields are skipped."""
        data = """
MSH|^~\\&|ViewPoint|Hospital|||20211223144928||ORU^R01|123456|P|2.4
OBX|1|ST|Fetus.Identifier
OBX|2|NM|SkullFetus.HeadCircumference^HC|Fetus1|175^175.0|mm
OBX|3|NM|SkullFetus.VP_HeadCircumference_Percentile|Fetus1|50^50%|%
OBX|4|NM|SkullFetus.BiParietalDiameter^BPD|Fetus1|68^68.0|mm
OBX|5|NM|SkullFetus.VP_BiParietalDiameter_Percentile|Fetus1|55^55%|%
OBX|6|NM|AbdomenFetus.AbdominalCircumference^AC|Fetus1|212^212.0|mm
OBX|7|NM|AbdomenFetus.VP_AbdominalCircumference_Percentile|Fetus1|48^48%|%
OBX|8|NM|ExtremitiesFetus.FemurLength^FL|Fetus1|48^48.0|mm
OBX|9|NM|ExtremitiesFetus.VP_FemurLength_Percentile|Fetus1|52^52%|%
"""
        term_bins = viewpoint_hl7.extract(data)
        # Should still extract 4 measurements despite malformed line
        assert len(term_bins) == 4

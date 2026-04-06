from unittest.mock import patch

import pytest

from backend.console.utils.star_name import get_hip_by_name, preprocess_name

# ---------------------------------------------------------------------------
# Fake HIP map used by get_hip_by_name tests (avoids reading the real file)
# Keys are the result of preprocess_name() applied to the original names.
# ---------------------------------------------------------------------------
_FAKE_MAP: dict[str, int] = {
    "rhovir":  82607,
    "31vir":   72220,
    "psivir":  72192,
    "betlib":  74785,
    "ome1aql": 97295,
}


class TestPreprocessName:
    """Unit tests for the normalisation logic (no I/O involved)."""

    @pytest.mark.parametrize("raw, expected", [
        ("ρ Vir",   "rhovir"),
        ("31Vir",   "31vir"),
        ("ψ Vir",   "psivir"),
        ("β Lib",   "betlib"),
        ("ω 1Aql",  "ome1aql"),
    ])
    def test_preprocess_name(self, raw: str, expected: str):
        assert preprocess_name(raw) == expected

    def test_none_returns_empty_string(self):
        assert preprocess_name(None) == ""

    def test_empty_string(self):
        assert preprocess_name("") == ""


class TestGetHipByName:
    """Unit tests for get_hip_by_name (file I/O mocked out)."""

    @pytest.fixture(autouse=True)
    def mock_map(self):
        """Patch _load_star_name_map so no real file is needed."""
        with patch(
            "backend.console.utils.star_name._load_star_name_map",
            return_value=_FAKE_MAP,
        ):
            yield

    @pytest.mark.parametrize("name, expected_hip", [
        ("ρ Vir",  82607),
        ("31Vir",  72220),
        ("ψ Vir",  72192),
        ("β Lib",  74785),
        ("ω 1Aql", 97295),
    ])
    def test_known_names(self, name: str, expected_hip: int):
        assert get_hip_by_name(name) == expected_hip

    def test_unknown_name_returns_none(self):
        assert get_hip_by_name("NonExistentStar XYZ") is None

    def test_lookup_is_case_insensitive(self):
        """Names differing only in case should resolve to the same HIP."""
        assert get_hip_by_name("RHO VIR") == get_hip_by_name("ρ Vir")

    def test_lookup_ignores_extra_spaces(self):
        assert get_hip_by_name("β  Lib") == 74785

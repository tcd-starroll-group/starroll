import re
import json
from pathlib import Path
from typing import Optional

# Module-level cache: the JSON file is read only once.
_star_name_to_hip: Optional[dict[str, int]] = None

_DATA_FILE = Path(__file__).parent.parent.parent / \
    "data" / "star_name_map.json"


def _load_star_name_map() -> dict[str, int]:
    global _star_name_to_hip
    if _star_name_to_hip is None:
        with open(_DATA_FILE, encoding="utf-8") as f:
            _star_name_to_hip = json.load(f)["map"]
    return _star_name_to_hip


def get_hip_by_name(name: str) -> Optional[int]:
    """Return the HIP number for a star name, or None if not found.

    The name is normalized via preprocess_name before lookup so that
    variations in spacing, case, and Greek-letter spelling are handled.
    """
    key = preprocess_name(name)
    return _load_star_name_map().get(key)


def preprocess_name(name: str) -> str:
    """Normalize a star name for mapping keys.

    Rules:
    1. Remove spaces and underscores
    2. Convert all letters to lowercase

    This function is kept separate for reuse.
    """
    if name is None:
        return ""
    # strip surrounding whitespace and quotes and lowercase early
    s = name.strip().strip('\"').strip("'").lower()

    # replace common Greek letters (symbols or full names) with dataset
    # abbreviations used in the raw files (e.g. 'gamma' or 'γ' -> 'gam')
    greek_replacements = [
        (r"\b(alpha|α)\b", "alf"),
        (r"\b(beta|β)\b", "bet"),
        (r"\b(gamma|γ)\b", "gam"),
        (r"\b(delta|δ)\b", "del"),
        (r"\b(epsilon|eps|ε)\b", "eps"),
        (r"\b(zeta|ζ)\b", "zet"),
        (r"\b(eta|η)\b", "eta"),
        (r"\b(theta|θ)\b", "the"),
        (r"\b(iota|ι)\b", "iot"),
        (r"\b(kappa|κ)\b", "kap"),
        (r"\b(lambda|λ)\b", "lam"),
        (r"\b(mu|μ)\b", "mu"),
        (r"\b(nu|ν)\b", "nu"),
        (r"\b(xi|ξ)\b", "ksi"),
        (r"\b(omicron|ο)\b", "omi"),
        (r"\b(pi|π)\b", "pi"),
        (r"\b(rho|ρ)\b", "rho"),
        (r"\b(sigma|σ|ς)\b", "sig"),
        (r"\b(tau|τ)\b", "tau"),
        (r"\b(upsilon|υ)\b", "ups"),
        (r"\b(phi|φ)\b", "phi"),
        (r"\b(chi|χ)\b", "chi"),
        (r"\b(psi|ψ)\b", "psi"),
        (r"\b(omega|ω)\b", "ome"),
    ]

    for patt, repl in greek_replacements:
        s = re.sub(patt, repl, s)

    # remove spaces, underscores and dots
    s = re.sub(r"[ _.]+", "", s)

    # remove leading zeros from numbers (e.g. ksi02 -> ksi2)
    s = re.sub(r"0+(\d)", r"\1", s)
    return s

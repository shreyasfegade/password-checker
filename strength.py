# strength.py
"""
Password charset & entropy utilities.

Functions provided:
- analyze_charset(password) -> dict of counts and flags
- estimate_charset_size(counts) -> int (approx charset size S)
- entropy_bits(password) -> float (L * log2(S))
- guesses_log10_from_entropy(entropy_bits) -> float (log10 of naive guesses)
- crack_times_for_speeds(entropy_bits, attacker_speeds) -> dict of times (seconds and human)
- format_seconds(seconds) -> human readable string
"""

import math

# approx sizes for character classes
CLASS_SIZES = {
    "lower": 26,
    "upper": 26,
    "digits": 10,
    "symbols": 33,
    "space": 1
}

def analyze_charset(password: str) -> dict:
    """Return counts and flags for character classes and length."""
    pw = password or ""
    length = len(pw)
    has_lower = any(c.islower() for c in pw)
    has_upper = any(c.isupper() for c in pw)
    has_digit = any(c.isdigit() for c in pw)
    has_space = any(c.isspace() for c in pw)
    has_symbol = any((not c.isalnum()) and (not c.isspace()) for c in pw)
    counts = {
        "length": length,
        "has_lower": has_lower,
        "has_upper": has_upper,
        "has_digit": has_digit,
        "has_symbol": has_symbol,
        "has_space": has_space,
    }
    return counts

def estimate_charset_size(counts: dict) -> int:
    """Estimate the charset size S based on which character classes are present."""
    s = 0
    if counts.get("has_lower"):
        s += CLASS_SIZES["lower"]
    if counts.get("has_upper"):
        s += CLASS_SIZES["upper"]
    if counts.get("has_digit"):
        s += CLASS_SIZES["digits"]
    if counts.get("has_symbol"):
        s += CLASS_SIZES["symbols"]
    if counts.get("has_space"):
        # spaces are rarely useful for entropy but count as 1
        s += CLASS_SIZES["space"]
    # if password empty, avoid s=0
    return max(s, 0)

def entropy_bits(password: str) -> float:
    """
    Compute naive entropy in bits: L * log2(S).
    This assumes each character is chosen uniformly from the estimated charset.
    """
    counts = analyze_charset(password)
    L = counts["length"]
    S = estimate_charset_size(counts)
    if L == 0 or S <= 1:
        return 0.0
    return L * math.log2(S)

def guesses_log10_from_entropy(entropy_bits: float) -> float:
    """
    Return log10 of the naive guess count: log10(2^entropy_bits) = entropy_bits * log10(2)
    Using log-space avoids overflow for large values.
    """
    return entropy_bits * math.log10(2)

def guesses_from_entropy_if_small(entropy_bits: float, threshold_bits: float = 60):
    """
    If entropy_bits is small enough (threshold_bits), return the exact guesses as an int.
    Otherwise, return None (use log representation instead).
    Default threshold 60 bits (~1.15e18 guesses).
    """
    if entropy_bits <= threshold_bits:
        # safe to compute exact number
        return 2 ** int(entropy_bits)
    return None

def format_seconds(seconds: float) -> str:
    """Human readable formatting for seconds (chooses up to years)."""
    if seconds < 1:
        return f"{seconds:.3f} seconds"
    minute = 60
    hour = 3600
    day = 86400
    year = 3600 * 24 * 365
    if seconds < minute:
        return f"{seconds:.2f} seconds"
    if seconds < hour:
        return f"{seconds/60:.2f} minutes"
    if seconds < day:
        return f"{seconds/3600:.2f} hours"
    if seconds < year:
        return f"{seconds/day:.2f} days"
    years = seconds / year
    if years < 1000:
        return f"{years:.2f} years"
    # use scientific for huge numbers
    return f"{years:.2e} years"

def crack_times_for_speeds(entropy_bits: float, attacker_speeds: dict) -> dict:
    """
    Given entropy_bits and a dict mapping label->guesses_per_second,
    return a dict mapping label -> { 'seconds': float, 'human': str, 'log10_seconds': float, 'log10_guesses': float }
    We compute in log-space to avoid overflow:
      log10(guesses) = entropy_bits * log10(2)
      log10(seconds) = log10(guesses) - log10(speed)
    seconds = 10**(log10_seconds) (only computed if not astronomically large)
    """
    out = {}
    log10_guesses = guesses_log10_from_entropy(entropy_bits)
    for label, speed in attacker_speeds.items():
        # handle zero or extremely small speed 
        if speed <= 0:
            out[label] = {"seconds": float("inf"), "human": "infinite (invalid speed)", "log10_seconds": float("inf"), "log10_guesses": log10_guesses}
            continue
        log10_speed = math.log10(speed)
        log10_seconds = log10_guesses - log10_speed
        # convert log10_seconds to seconds
        if log10_seconds < 300:  # 10^300 is absurd; above that keep as infinity/scientific
            seconds = 10 ** log10_seconds
            human = format_seconds(seconds)
        else:
            seconds = float("inf")
            # represent large time using years
            human = ">10^300 seconds (astronomical)"
        out[label] = {
            "seconds": seconds,
            "human": human,
            "log10_seconds": log10_seconds,
            "log10_guesses": log10_guesses
        }
    return out

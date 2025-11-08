# hashing_demo.py
"""
Hashing demo helpers.
Provides:
- safe hash functions (md5, sha256, bcrypt, argon2)
- approximate attacker hash/rate presets for offline cracking per algorithm
- utility get_hash_speed(algorithm, params) -> guesses_per_second (approx)
"""

import hashlib
import math
import time

# bcrypt and argon2 are optional; imported with try/except so UI can fallback gracefully.
try:
    import bcrypt
except Exception:
    bcrypt = None

try:
    from argon2 import PasswordHasher
    ARGON2_AVAILABLE = True
except Exception:
    PasswordHasher = None
    ARGON2_AVAILABLE = False

#simple wrappers to show example hashed outputs 
def hash_md5(password: str) -> str:
    return hashlib.md5(password.encode("utf-8")).hexdigest()

def hash_sha256(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def hash_bcrypt(password: str, rounds: int = 12) -> str:
    if bcrypt is None:
        raise RuntimeError("bcrypt not available in this environment.")
    salt = bcrypt.gensalt(rounds=rounds)
    out = bcrypt.hashpw(password.encode("utf-8"), salt)
    return out.decode()

def hash_argon2(password: str, time_cost: int = 2, memory_cost_kb: int = 102400) -> str:
    # memory_cost_kb default ~100MB (102400 KB)
    if not ARGON2_AVAILABLE:
        raise RuntimeError("argon2 not available in this environment.")
    ph = PasswordHasher(time_cost=time_cost, memory_cost=memory_cost_kb // 1024)  # argon2-cffi PasswordHasher expects memory_cost in MB
    return ph.hash(password)

#example attacker speeds (guesses per second) for **offline** attacks
OFFLINE_HASH_SPECS = {
    "Raw fast hash (MD5/SHA1) - single GPU": {
        "speed": 1e9,   
        "note": "Raw fast hashes on high-end GPU"
    },
    "Raw fast hash (MD5/SHA1) - multi GPU cluster": {
        "speed": 1e13,  
        "note": "Large GPU cluster for raw fast hashes"
    },
    "SHA256 (fast) - single GPU": {
        "speed": 5e8,
        "note": "SHA256 optimized on GPU"
    },
    "bcrypt (cost=12) - single CPU core": {
        "speed": 200,   
        "note": "bcrypt is intentionally slow; CPU-bound"
    },
    "bcrypt (cost=12) - large botnet": {
        "speed": 2000,
        "note": "Many CPUs combined"
    },
    "argon2 (moderate) - single machine": {
        "speed": 50,
        "note": "Argon2 with moderate params — memory-hard"
    },
    "argon2 (moderate) - cluster": {
        "speed": 500,
        "note": "Distributed cluster of machines"
    }
}

# return an approx guesses/sec for chosen storage hash type and params.
def get_hash_speed(algorithm_key: str, bcrypt_rounds: int = 12, argon2_time_cost: int = 2, argon2_mem_kb: int = 102400) -> float:
    """
    Return guesses/sec for the chosen 'algorithm_key' string (one of the keys in OFFLINE_HASH_SPECS).
    We scale bcrypt speed by 2^(12 - rounds) roughly (very rough).
    For argon2 we scale inversely with time_cost.
    This function intentionally returns conservative illustrative speeds and must be presented as examples.
    """
    # exact mapping if key present
    spec = OFFLINE_HASH_SPECS.get(algorithm_key)
    if spec:
        base = spec["speed"]
    else:
        # fallback: treat as raw fast hash
        base = 1e8
    # adjust for bcrypt rounds (higher rounds -> slower)
    if "bcrypt" in algorithm_key.lower():
        # every increase of 1 round halves speed (approx)
        rounds_diff = bcrypt_rounds - 12
        adjust = 2 ** (-rounds_diff)
        return max(1.0, base * adjust)
    if "argon2" in algorithm_key.lower():
        # scale inversely with time_cost (very rough)
        adjust = 1.0 / max(1, argon2_time_cost)
        return max(0.1, base * adjust)
    return base


def format_seconds(seconds: float) -> str:
    if seconds == float("inf") or seconds != seconds:
        return "infinite / unknown"
    if seconds < 1:
        return f"{seconds:.3f} s"
    minute = 60
    hour = 3600
    day = 86400
    year = 3600 * 24 * 365
    if seconds < minute:
        return f"{seconds:.2f} s"
    if seconds < hour:
        return f"{seconds/60:.2f} min"
    if seconds < day:
        return f"{seconds/3600:.2f} h"
    if seconds < year:
        return f"{seconds/day:.2f} days"
    years = seconds / year
    return f"{years:.2f} years"

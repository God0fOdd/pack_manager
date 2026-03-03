import hashlib
import random
import secrets
import string


def generate_password(
    length: int = 18,
    use_upper: bool = True,
    use_lower: bool = True,
    use_digits: bool = True,
    use_symbols: bool = True,
    salt: str = "",
    deterministic_seed: str = "",
) -> str:
    pool = ""
    if use_upper:
        pool += string.ascii_uppercase
    if use_lower:
        pool += string.ascii_lowercase
    if use_digits:
        pool += string.digits
    if use_symbols:
        pool += "!@#$%^&*()-_=+[]{};:,.?"

    if not pool:
        raise ValueError("Select at least one character set.")

    if deterministic_seed:
        digest = hashlib.sha256(f"{deterministic_seed}|{salt}".encode("utf-8")).digest()
        seed = int.from_bytes(digest, "big")
        rng = random.Random(seed)
        return "".join(rng.choice(pool) for _ in range(length))

    salt_bytes = hashlib.sha256(salt.encode("utf-8")).digest() if salt else b""
    chars = []
    for i in range(length):
        entropy = secrets.token_bytes(32) + salt_bytes + i.to_bytes(2, "big")
        idx = int.from_bytes(hashlib.sha256(entropy).digest(), "big") % len(pool)
        chars.append(pool[idx])
    return "".join(chars)

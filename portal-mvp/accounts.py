"""Account authentication: username/password login for the demo portal.

Kept separate from credentials.py (VC/VP trust logic) and portal.py (API
wiring), same split as the existing codebase. No extra dependency: uses
hashlib.pbkdf2_hmac from the standard library instead of bcrypt/argon2.
"""
import hashlib
import hmac
import os
import re

ITERATIONS = 200_000
USERNAME_RE = re.compile(r'^[a-zA-Z0-9_.-]{3,32}$')


def valid_username(name):
    return isinstance(name, str) and bool(USERNAME_RE.fullmatch(name))


def valid_password(password):
    return isinstance(password, str) and 8 <= len(password) <= 128


def hash_password(password):
    salt = os.urandom(16)
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return salt.hex(), digest.hex()


def verify_password(password, salt_hex, hash_hex):
    """Constant-time compare. Never raises on malformed stored values."""
    try:
        salt = bytes.fromhex(salt_hex)
        expected = bytes.fromhex(hash_hex)
    except (ValueError, TypeError):
        return False
    digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, ITERATIONS)
    return hmac.compare_digest(digest, expected)

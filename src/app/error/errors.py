from enum import Enum
from dataclasses import dataclass

class ErrorKind(str, Enum):
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    PERMISSION = "permission_denied"
    UNAVAILABLE = "unavailable"
    INTERNAL = "internal"

@dataclass
class DomainException(Exception):
    kind: ErrorKind = ErrorKind.INTERNAL
    message: str = ""
from __future__ import annotations

from enum import Enum


class DomainAuditActorType(str, Enum):
    USER = "user"
    SERVICE = "service"


class DomainRiskSeverity(str, Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class DomainRiskCategory(str, Enum):
    RISK = "risk"
    EXECUTION = "execution"
    SESSION = "session"


class ReconciliationStatus(str, Enum):
    IN_SYNC = "in_sync"
    SAFE_MODE_REQUIRED = "safe_mode_required"
    PANIC_STOP_REQUIRED = "panic_stop_required"

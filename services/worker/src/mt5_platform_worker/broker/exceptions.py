from __future__ import annotations


class MT5BrokerError(Exception):
    def __init__(
        self,
        message: str,
        *,
        operation: str | None = None,
        last_error_code: int | None = None,
        last_error_description: str | None = None,
        retcode: int | None = None,
        broker_comment: str | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.operation = operation
        self.last_error_code = last_error_code
        self.last_error_description = last_error_description
        self.retcode = retcode
        self.broker_comment = broker_comment


class MT5DependencyError(MT5BrokerError):
    pass


class MT5InitializationError(MT5BrokerError):
    pass


class MT5LoginError(MT5BrokerError):
    pass


class MT5OrderSendError(MT5BrokerError):
    pass

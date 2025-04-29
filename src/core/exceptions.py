from unittest.mock import Base


class BaseApiException(Exception):
    def __init__(self, message: str, status_code: int):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class JSONException(BaseApiException): ...


class ValueNotFoundException(BaseApiException): ...


class CRMTokenException(BaseApiException): ...


class CRMNotFoundException(BaseApiException): ...


class DuplicateImportException(BaseApiException): ...


class ImportContactsException(BaseApiException): ...


class ExportContactsException(BaseApiException):...

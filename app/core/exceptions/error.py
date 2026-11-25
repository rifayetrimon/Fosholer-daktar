class AppError(Exception):
    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(detail)


class NotFoundError(AppError):
    def __init__(self, detail: str = "Not found"):
        super().__init__(detail)


class ConflictError(AppError):
    def __init__(self, detail: str = "Conflict"):
        super().__init__(detail)


class UnauthorizedError(AppError):
    def __init__(self, detail: str = "Could not validate credentials"):
        super().__init__(detail)


class ForbiddenError(AppError):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(detail)


class LLMUnavailableError(AppError):
    def __init__(self, detail: str = "LLM service unavailable"):
        super().__init__(detail)

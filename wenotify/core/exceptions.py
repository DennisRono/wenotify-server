from typing import Any, Dict, List, Optional, Union
import traceback
from enum import Enum as PyEnum

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.exc import SQLAlchemyError, IntegrityError, OperationalError

from wenotify.core.logging import logger


class ErrorSource(str, PyEnum):
    """Enum for error sources."""

    VALIDATION = "validation"
    BUSINESS_LOGIC = "business_logic"
    SYSTEM = "system"
    AUTHORIZATION = "authorization"
    NOT_FOUND = "not_found"
    DATABASE = "database"
    INTEGRATION = "integration"
    RATE_LIMIT = "rate_limit"
    RESOURCE_LIMIT = "resource_limit"
    PAYMENT = "payment"
    DEPLOYMENT = "deployment"


class ErrorDetail(BaseModel):
    """Model for error details."""

    loc: Optional[List[str]] = None
    msg: str
    type: Optional[str] = None


class ErrorResponse(BaseModel):
    """Standardized error response model."""

    status_code: int
    error_code: str
    error_source: ErrorSource
    message: str
    details: Optional[List[Union[ErrorDetail, Dict[str, Any]]]] = None
    request_id: Optional[str] = None


class BaseAPIException(Exception):
    """Base API exception class."""

    status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code: str = "INTERNAL_SERVER_ERROR"
    error_source: ErrorSource = ErrorSource.SYSTEM
    default_message: str = "An unexpected error occurred"

    def __init__(
        self,
        message: Optional[str] = None,
        details: Optional[List[Union[ErrorDetail, Dict[str, Any]]]] = None,
        headers: Optional[Dict[str, Any]] = None,
    ):
        self.message = message or self.default_message
        self.details = details
        self.headers = headers
        super().__init__(self.message)

    def to_response(self, request: Request) -> JSONResponse:
        """Convert exception to a standardized JSON response."""
        return JSONResponse(
            status_code=self.status_code,
            content=ErrorResponse(
                status_code=self.status_code,
                error_code=self.error_code,
                error_source=self.error_source,
                message=self.message,
                details=self.details,
                request_id=request.headers.get("X-Request-ID"),
            ).model_dump(),
            headers=self.headers,
        )


class NotFoundError(BaseAPIException):
    """Resource not found exception."""

    status_code = status.HTTP_404_NOT_FOUND
    error_code = "NOT_FOUND"
    error_source = ErrorSource.NOT_FOUND
    default_message = "Resource not found"

    def __init__(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        **kwargs,
    ):
        message = kwargs.pop("message", None)
        if resource_type and resource_id and not message:
            message = f"{resource_type} with id {resource_id} not found"
        super().__init__(message=message, **kwargs)


class AuthenticationError(BaseAPIException):
    """Authentication error exception."""

    status_code = status.HTTP_401_UNAUTHORIZED
    error_code = "AUTHENTICATION_ERROR"
    error_source = ErrorSource.AUTHORIZATION
    default_message = "Authentication failed"

    def __init__(self, **kwargs):
        headers = kwargs.pop("headers", {})
        headers["WWW-Authenticate"] = "Bearer"
        super().__init__(headers=headers, **kwargs)


class AuthorizationError(BaseAPIException):
    """Authorization error exception."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "AUTHORIZATION_ERROR"
    error_source = ErrorSource.AUTHORIZATION
    default_message = "Not authorized to perform this action"


class ValidationError(BaseAPIException):
    """Validation error exception."""

    status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
    error_code = "VALIDATION_ERROR"
    error_source = ErrorSource.VALIDATION
    default_message = "Validation error"


class RateLimitExceededError(BaseAPIException):
    """Rate limit exceeded exception."""

    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    error_code = "RATE_LIMIT_EXCEEDED"
    error_source = ErrorSource.RATE_LIMIT
    default_message = "Rate limit exceeded. Please try again later."


class PaymentRequiredError(BaseAPIException):
    """Payment required exception."""

    status_code = status.HTTP_402_PAYMENT_REQUIRED
    error_code = "PAYMENT_REQUIRED"
    error_source = ErrorSource.PAYMENT
    default_message = "Payment required to access this resource"


class ResourceLimitExceededError(BaseAPIException):
    """Resource limit exceeded exception."""

    status_code = status.HTTP_403_FORBIDDEN
    error_code = "RESOURCE_LIMIT_EXCEEDED"
    error_source = ErrorSource.RESOURCE_LIMIT
    default_message = "Resource limit exceeded"


class BusinessLogicError(BaseAPIException):
    """Business logic error exception."""

    status_code = status.HTTP_400_BAD_REQUEST
    error_code = "BUSINESS_LOGIC_ERROR"
    error_source = ErrorSource.BUSINESS_LOGIC
    default_message = "Business logic error"


class DatabaseError(BaseAPIException):
    """Database error exception."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "DATABASE_ERROR"
    error_source = ErrorSource.DATABASE
    default_message = "Database error occurred"


class DatabaseIntegrityError(DatabaseError):
    """Database integrity error exception."""

    status_code = status.HTTP_409_CONFLICT
    error_code = "DATABASE_INTEGRITY_ERROR"
    default_message = "Database constraint violation"


class DatabaseConnectionError(DatabaseError):
    """Database connection error exception."""

    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    error_code = "DATABASE_CONNECTION_ERROR"
    default_message = "Database service is currently unavailable"


class IntegrationError(BaseAPIException):
    """Integration error exception."""

    status_code = status.HTTP_502_BAD_GATEWAY
    error_code = "INTEGRATION_ERROR"
    error_source = ErrorSource.INTEGRATION
    default_message = "Integration error"


class DeploymentError(BaseAPIException):
    """Deployment error exception."""

    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
    error_code = "DEPLOYMENT_ERROR"
    error_source = ErrorSource.DEPLOYMENT
    default_message = "Deployment failed"


def setup_exception_handlers(app: FastAPI) -> None:
    """Set up exception handlers for the application."""

    @app.exception_handler(BaseAPIException)
    async def handle_base_api_exception(
        request: Request, exc: BaseAPIException
    ) -> JSONResponse:
        """Handle all custom API exceptions."""

        if exc.status_code >= 500:
            logger.error(f"{exc.error_code}: {exc.message}")
        elif exc.status_code >= 400:
            logger.warning(f"{exc.error_code}: {exc.message}")
        else:
            logger.info(f"{exc.error_code}: {exc.message}")

        return exc.to_response(request)

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Handle Pydantic validation errors."""
        logger.warning(f"Validation error: {exc.errors()}")

        details = []
        for error in exc.errors():
            details.append(
                ErrorDetail(
                    loc=error.get("loc", []),
                    msg=error.get("msg", ""),
                    type=error.get("type", ""),
                )
            )

        validation_error = ValidationError(
            message="Request validation error", details=details
        )
        return validation_error.to_response(request)

    @app.exception_handler(SQLAlchemyError)
    async def handle_sqlalchemy_error(
        request: Request, exc: SQLAlchemyError
    ) -> JSONResponse:
        """Handle SQLAlchemy errors."""
        error_traceback = traceback.format_exc()
        logger.error(f"Database error: {str(exc)}\n{error_traceback}")

        if isinstance(exc, IntegrityError):
            error_message = str(exc)
            if "unique constraint" in error_message.lower():
                message = "A record with this information already exists"
            else:
                message = "Database constraint violation"

            db_error = DatabaseIntegrityError(message=message)
        elif isinstance(exc, OperationalError):
            db_error = DatabaseConnectionError()
        else:
            db_error = DatabaseError()

        return db_error.to_response(request)

    @app.exception_handler(Exception)
    async def handle_general_exception(
        request: Request, exc: Exception
    ) -> JSONResponse:
        """Handle all unhandled exceptions."""
        error_traceback = traceback.format_exc()
        logger.error(f"Unhandled exception: {str(exc)}\n{error_traceback}")

        generic_error = BaseAPIException()
        return generic_error.to_response(request)

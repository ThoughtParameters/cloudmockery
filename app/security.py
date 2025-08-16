"""
Security module for handling authentication and authorization.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.config import get_settings

# The auto_error=False means the dependency won't raise an error itself
# if the Authorization header is missing. This allows us to provide a
# custom error message.
bearer_scheme = HTTPBearer(auto_error=False)

def verify_token(
    token: HTTPAuthorizationCredentials = Depends(bearer_scheme)
):
    """
    FastAPI dependency to verify the mock bearer token.

    This function checks for a valid 'Authorization: Bearer <token>' header
    and validates the token against the one defined in the application settings.

    Raises:
        HTTPException(401): If the token is missing or invalid.
    """
    settings = get_settings()
    if token is None or token.credentials != settings.MOCK_AUTH_TOKEN:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token.credentials

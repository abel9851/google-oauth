import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, Optional

import jwt
from app.config import settings
from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyCookie

# Cookie-based JWT authentication
oauth2_scheme = APIKeyCookie(name="session_token")


def create_access_token(
    data: Dict[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """
    Create a new JWT token

    Args:
        data: Dictionary containing claims to be encoded in the JWT
        expires_delta: Optional timedelta object to override the default expiration time

    Returns:
        JWT token as string
    """
    to_encode = data.copy()

    # Set expiration time
    expire = datetime.utcnow() + (
        expires_delta
        if expires_delta
        else timedelta(minutes=settings.JWT_EXPIRE_MINUTES)
    )

    # Add standard claims
    to_encode.update(
        {
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": str(uuid.uuid4()),  # JWT ID for uniqueness
            "kid": "auth-server-1",  # Key ID for key rotation
        }
    )

    # Encode with the JWT secret
    encoded_jwt = jwt.encode(
        to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM
    )

    return encoded_jwt


def verify_token(token: str) -> Dict[str, Any]:
    """
    Verify and decode JWT token

    Args:
        token: JWT token to verify

    Returns:
        Dict containing the decoded claims

    Raises:
        HTTPException: If token is invalid or expired
    """
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM]
        )
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(token: str = Depends(oauth2_scheme)) -> Dict[str, Any]:
    """
    FastAPI dependency to get current user from JWT token

    Args:
        token: JWT token extracted from cookie

    Returns:
        Dict containing user information

    Raises:
        HTTPException: If token is invalid or user not found
    """
    # Verify the token
    payload = verify_token(token)

    # Return user ID and role
    return {
        "user_id": payload.get("sub"),
        "role": payload.get("role", "user"),
        "email": payload.get("email"),
    }

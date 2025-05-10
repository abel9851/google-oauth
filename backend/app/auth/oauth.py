from datetime import datetime, timedelta
from typing import Optional
from urllib.parse import urlencode

import requests
from app.auth.jwt import create_access_token
from app.auth.utils import (
    create_auth_cookies,
    encrypt_refresh_token,
    generate_nonce,
    generate_state,
    verify_id_token,
)
from app.config import settings
from app.db.database import get_db
from app.models.user import User
from fastapi import APIRouter, Cookie, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

router = APIRouter(prefix="/oauth", tags=["oauth"])


@router.get("/authorize")
async def authorize(response: Response, db: Session = Depends(get_db)):
    """
    Redirect to Google's OAuth authorization endpoint

    - Generates a state parameter and stores it in a cookie for CSRF protection
    - Generates a nonce parameter for PKCE
    - Builds the authorization URL with required parameters
    - Returns a 302 redirect to Google's authorization page
    """
    # Generate state and nonce
    state = generate_state()
    nonce = generate_nonce()

    # Set state in a secure cookie
    response.set_cookie(
        key="oauth_state",
        value=state,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=600,  # 10 minutes
        path="/oauth2/callback",
    )

    # Set nonce in a secure cookie
    response.set_cookie(
        key="oauth_nonce",
        value=nonce,
        httponly=True,
        secure=settings.COOKIE_SECURE,
        samesite="lax",
        max_age=600,  # 10 minutes
        path="/oauth2/callback",
    )

    # Build authorization URL
    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": f"{settings.BASE_URL}/oauth2/callback",
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",  # For refresh token
        "prompt": "consent",  # Always ask for consent to ensure we get refresh token
        "state": state,
        "nonce": nonce,
    }

    auth_url = f"{settings.GOOGLE_AUTH_URL}?{urlencode(params)}"

    # Redirect to Google's auth page
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = auth_url

    return {"message": "Redirecting to Google for authentication"}


@router.get("/oauth2/callback")
async def oauth_callback(
    code: str,
    state: str,
    response: Response,
    oauth_state: Optional[str] = Cookie(None),
    oauth_nonce: Optional[str] = Cookie(None),
    db: Session = Depends(get_db),
):
    """
    Handle the OAuth callback from Google

    - Validates the state parameter against the cookie
    - Exchanges the authorization code for tokens
    - Verifies the ID token
    - Upserts the user in the database
    - Creates a session JWT token and sets it as a cookie
    - Encrypts and stores the refresh token in the database
    - Redirects to the frontend homepage
    """
    # Validate state to prevent CSRF
    if not oauth_state or oauth_state != state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter"
        )

    # Exchange authorization code for tokens
    token_response = requests.post(
        settings.GOOGLE_TOKEN_URL,
        data={
            "code": code,
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "redirect_uri": f"{settings.BASE_URL}/oauth2/callback",
            "grant_type": "authorization_code",
        },
    )

    if token_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Token exchange failed: {token_response.text}",
        )

    token_data = token_response.json()

    # Extract tokens
    id_token = token_data.get("id_token")
    access_token = token_data.get("access_token")
    refresh_token = token_data.get("refresh_token")

    if not id_token or not access_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required tokens in response",
        )

    # Verify ID token
    try:
        id_token_payload = verify_id_token(id_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid ID token: {str(e)}",
        )

    # Check nonce in ID token
    if oauth_nonce and id_token_payload.get("nonce") != oauth_nonce:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid nonce in ID token"
        )

    # Extract user info from ID token
    user_email = id_token_payload.get("email")
    google_id = id_token_payload.get("sub")
    name = id_token_payload.get("name")
    picture = id_token_payload.get("picture")

    if not user_email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing required user information in ID token",
        )

    # Find or create user
    user = db.query(User).filter(User.google_id == google_id).first()

    if not user:
        # Create new user
        user = User(email=user_email, google_id=google_id, name=name, picture=picture)
        db.add(user)
    else:
        # Update existing user
        user.email = user_email
        user.name = name
        user.picture = picture

    # Store encrypted refresh token if provided
    if refresh_token:
        # Calculate token expiration (usually 6 months for Google)
        refresh_token_expires_at = datetime.utcnow() + timedelta(days=180)

        # Encrypt the refresh token
        encrypted_token, token_iv, token_tag = encrypt_refresh_token(refresh_token)

        user.encrypted_refresh_token = encrypted_token
        user.refresh_token_iv = token_iv
        user.refresh_token_tag = token_tag
        user.refresh_token_expires_at = refresh_token_expires_at

    # Commit user to database
    db.commit()
    db.refresh(user)

    # Create JWT for session
    jwt_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": "user",
        "name": user.name,
        "picture": user.picture,
    }

    session_token = create_access_token(jwt_data)

    # Clear OAuth cookies
    response.delete_cookie(key="oauth_state", path="/oauth2/callback")
    response.delete_cookie(key="oauth_nonce", path="/oauth2/callback")

    # Set auth cookies
    cookies = create_auth_cookies(session_token)
    for cookie_name, cookie_data in cookies.items():
        response.set_cookie(**cookie_data)

    # Redirect to frontend
    response.status_code = status.HTTP_302_FOUND
    response.headers["Location"] = f"{settings.FRONTEND_URL}/?login=success"

    return {"message": "Authentication successful"}


# https://support.google.com/cloud/answer/15549257?hl=ko&visit_id=638819651878336340-597981199&rd=1#zippy=%2Cnative-applications-android-ios-desktop-uwp-chrome-extensions-tv-and-limited-input%2Cweb-applications

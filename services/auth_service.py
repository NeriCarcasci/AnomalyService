from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader

API_KEY = "mySuperSecureAndSecretAPIKey"
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=True)

class AuthService:
    @staticmethod
    def authenticate(api_key: str = Security(api_key_header)):
        """Authenticates requests using an API key."""
        if api_key != API_KEY:
            raise HTTPException(status_code=401, detail="Unauthorized: Invalid API Key")
        return True
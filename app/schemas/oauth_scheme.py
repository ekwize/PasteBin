from .base_scheme import Base


class AccessToken(Base):
    access_token: str
    token_type: str = "Bearer"


class Tokens(Base):
    access_token: str
    refresh_token: str
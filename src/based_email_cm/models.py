import datetime
import re
import typing as ty
import uuid

from argon2 import PasswordHasher
from pydantic import validator, validate_email, Field, EmailStr

from based_email_cm import common

_USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
_USERNAME_RE = re.compile(_USERNAME_PATTERN)


@common.nats_kv_bucket('users', 'username')
class User(common.BaseModel):
    username: ty.Annotated[str, Field(regex=_USERNAME_PATTERN)]
    password_hash: str
    email: ty.Annotated[EmailStr, Field(validator=validate_email)]
    is_superuser: bool
    date_joined: datetime.datetime

    @validator('name')
    def _username_safe(cls, v):
        if _USERNAME_RE.match(v) is None:
            raise ValueError('invalid username')
        return v.title()

    def validate_password(self, ph: PasswordHasher, password: str) -> bool:
        return ph.verify(self.password_hash, password)

    def needs_rehash(self, ph: PasswordHasher) -> bool:
        return ph.check_needs_rehash(self.password_hash)


@common.nats_kv_bucket('invites', 'code')
class Invite(common.BaseModel):
    email: ty.Annotated[EmailStr, Field(validator=validate_email)]
    code: ty.Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)]
    date_sent: datetime.datetime
    date_expired: datetime.datetime

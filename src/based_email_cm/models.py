import datetime
import re
import typing as ty
import uuid

from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from pydantic import EmailStr, Field, validate_email, validator

from based_email_cm import common

_USERNAME_PATTERN = r'^[a-zA-Z0-9_]+$'
USERNAME_RE = re.compile(_USERNAME_PATTERN)

USER_BUCKET = 'users'
USER_MAP_BUCKET = 'user-id-map'

# @common.nats_kv_bucket(USER_BUCKET, 'id')


class User(common.BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    username: ty.Annotated[str, Field(regex=_USERNAME_PATTERN)]
    password_hash: str
    email: ty.Annotated[EmailStr, Field(validator=validate_email)]
    is_superuser: bool
    date_joined: datetime.datetime

    @validator('username')
    def _username_safe(cls, v):
        if USERNAME_RE.match(v) is None:
            raise ValueError('invalid username')
        return v

    def validate_password(self, ph: PasswordHasher, password: str) -> bool:
        try:
            return ph.verify(self.password_hash, password)
        except VerificationError:
            return False

    def needs_rehash(self, ph: PasswordHasher) -> bool:
        return ph.check_needs_rehash(self.password_hash)

    def rehash(self, ph: PasswordHasher, password: str) -> None:
        self.password_hash = ph.hash(password)


# @common.nats_kv_bucket('invites', 'code')
class Invite(common.BaseModel):
    email: ty.Annotated[EmailStr, Field(validator=validate_email)]
    code: ty.Annotated[uuid.UUID, Field(default_factory=uuid.uuid4)]
    date_sent: datetime.datetime
    date_expired: datetime.datetime

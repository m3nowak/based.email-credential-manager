import json
import typing as ty

import nats.aio.client
import nats.js.errors
from argon2 import PasswordHasher
from litestar import Controller, Response, post
from pydantic import validator

from based_email_cm import models
from based_email_cm.common import BaseModel


class LoginRequest(BaseModel):
    '''Request to login'''
    username: str
    password: str
    nkey: str

    @validator('username')
    def _username_safe(cls, v):
        if models.USERNAME_RE.match(v) is None:
            raise ValueError('invalid username')
        return v

    @validator('nkey')
    def _nkey_ok(cls, v):
        if len(v) != 56 or not v.startswith('U'):
            raise ValueError('invalid nkey')
        return v


class LoginResponse(BaseModel):
    '''Response to a request to login'''
    success: bool
    error: ty.Optional[str]
    jwt: ty.Optional[str]


def login_failure() -> Response[LoginResponse]:
    return Response(LoginResponse(success=False, error='Bad credentials', jwt=None), status_code=400)


class LoginController(Controller):
    path = "/login"

    @post()
    async def login(self, data: LoginRequest, nc: nats.aio.client.Client, ph: PasswordHasher)\
            -> Response[LoginResponse]:
        js = nc.jetstream()
        user_id_map_bucket = await js.key_value(models.USER_MAP_BUCKET)
        user_bucket = await js.key_value(models.USER_BUCKET)
        try:
            user_id_raw = await user_id_map_bucket.get(data.username)
        except nats.js.errors.KeyValueError:
            user_id_raw = None
        if user_id_raw is None or user_id_raw.value is None:
            return login_failure()
        try:
            user_raw = await user_bucket.get(user_id_raw.value.decode('utf-8'))
        except nats.js.errors.KeyValueError:
            user_raw = None
        if user_raw is None or user_raw.value is None:
            return login_failure()
        else:
            user = models.User.parse_raw(user_raw.value)
            if not user.validate_password(ph, data.password):
                return login_failure()
            else:
                if user.needs_rehash(ph):
                    user.rehash(ph, data.password)
                    await user_bucket.put(data.username, json.dumps(user.dict()).encode('utf-8'))
                return Response(LoginResponse(success=True, error=None, jwt=None), status_code=200)  # TODO generate jwt

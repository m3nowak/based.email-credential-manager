from dataclasses import dataclass

from nats_nsc import Account, Operator

from based_email_cm import config


@dataclass
class JwtCtx:
    account: Account
    operator: Operator

    @classmethod
    def from_config(cls, config: config.Config):
        if config.userspace_account_jwt_path is None or config.userspace_account_key_path is None:
            raise ValueError("Account JWT or Key path is not set")
        opr = Operator(open(config.operator_jwt_path).read())
        acc = Account(open(config.userspace_account_jwt_path).read(), open(config.userspace_account_key_path).read())

        return cls(account = acc, operator = opr)

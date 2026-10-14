from dataclasses import dataclass

from typing_extensions import override

from bissap.auditing.exploit_step import ExploitStep
from bissap.authorization import AuthorizationObject


@dataclass(frozen=True)
class AuthorizationStep(ExploitStep):
    authorization: AuthorizationObject

    @override
    def is_usable_by(self, profiles: set[str]) -> bool:
        return self.authorization.profiles_has_authorization(profiles)

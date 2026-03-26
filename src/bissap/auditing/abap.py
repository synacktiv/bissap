from dataclasses import dataclass, field

from typing_extensions import override

from bissap.auditing.exploit_step import ExploitStep
from bissap.auditing.transaction import SM49, SM69, Transaction
from bissap.authorization import (
    ACTVT,
    CFUNCNAME,
    COMMAND,
    DEVCLASS,
    FILENAME,
    OBJNAME,
    OBJTYPE,
    PROGRAM,
    S_C_FUNCT,
    S_DATASET,
    S_DEVELOP,
    S_LOG_COM,
    S_RZL_ADM,
    AuthorizationObject,
)


@dataclass(frozen=True)
class Report(ExploitStep):
    name: str
    description: str | None = None
    package: str | None = None
    transactions: frozenset[Transaction] = field(default_factory=frozenset)
    additionnal_authorizations: frozenset[AuthorizationObject] = field(
        default_factory=frozenset
    )

    @override
    def is_usable_by(self, profiles: set[str]):
        read_program_auth = {
            OBJNAME(self.name),
            OBJTYPE('PROG'),
            ACTVT('03'),
        }
        if self.package is not None:
            read_program_auth.add(DEVCLASS(self.package))

        authorizations = {
            S_DEVELOP(read_program_auth),
            S_DEVELOP({OBJTYPE('PROG'), OBJNAME(self.name), ACTVT('16')}),
        } | self.additionnal_authorizations

        if not all(
            auth.profiles_has_authorization(profiles) for auth in authorizations
        ):
            return False

        if not all(
            transaction.is_usable_by(profiles) for transaction in self.transactions
        ):
            return False

        return True


RSBDCOS0 = Report(
    'RSBDCOS0',
    'Execute OS command from SAP GUI',
    package='SBDC',
    transactions=frozenset({SM69, SM49}),
    additionnal_authorizations=frozenset(
        {
            S_C_FUNCT({PROGRAM('RSBDCOS0'), ACTVT('16'), CFUNCNAME('SYSTEM')}),
            # Technically, HOST and OPSYSTEM are needed fields in S_LOG_COM, but it is dependent on the host and we can't know it beforehand.
            S_LOG_COM({COMMAND('RSBDCOS0')}),
            S_RZL_ADM({ACTVT('01')}),
        }
    ),
)

RS_LXE_EXTRACT_OL2CSV = Report(
    'RS_LXE_EXTRACT_OL2CSV',
    package='SLXE',
)

ARCHIVFILE_SERVER_TO_CLIENT = Report(
    'ARCHIVFILE_SERVER_TO_CLIENT',
    additionnal_authorizations=frozenset(
        {S_DATASET({ACTVT('33'), FILENAME('/usr/sap/*')})}
    ),
)

from dataclasses import dataclass, field

from typing_extensions import override

from bissap.auditing.exploit_step import ExploitStep
from bissap.authorization import (
    ACTVT,
    OBJTYPE,
    RFC_NAME,
    S_DEVELOP,
    S_RFC,
    AuthorizationObject,
)


@dataclass(frozen=True)
class Rfc(ExploitStep):
    authorization: AuthorizationObject
    additionnal_authorizations: frozenset[AuthorizationObject] = field(
        default_factory=frozenset
    )

    def __post_init__(self):
        assert self.authorization.name == 'S_RFC'
        assert len(self.authorization.fields) <= 3
        assert 'RFC_NAME' in {f.name for f in self.authorization.fields}
        assert {f.name for f in self.authorization.fields}.issubset(
            {
                'RFC_TYPE',
                'RFC_NAME',
                'ACTVT',
            }
        )

    @property
    def name(self):
        return next(f.value for f in self.authorization.fields if f.name == 'RFC_NAME')

    @classmethod
    def from_rfc_name(
        cls,
        rfc_name: str,
        additionnal_authorizations: frozenset[AuthorizationObject] = frozenset(),
    ):
        return cls(S_RFC({RFC_NAME(rfc_name), ACTVT('16')}), additionnal_authorizations)

    @override
    def is_usable_by(self, profiles: set[str]):
        return self.authorization.profiles_has_authorization(profiles) and all(
            auth.profiles_has_authorization(profiles)
            for auth in self.additionnal_authorizations
        )


_rfc = Rfc.from_rfc_name


# RFC_ABAP_INSTALL_AND_RUN generates and runs arbitrary ABAP code, which also
# requires the authorization to create a program (S_DEVELOP).
RFC_ABAP_INSTALL_AND_RUN = _rfc(
    'RFC_ABAP_INSTALL_AND_RUN',
    frozenset({S_DEVELOP({OBJTYPE('PROG'), ACTVT('01')})}),
)


# The BAPIs used by SU01 to assign profiles/roles can also be called directly through RFC.
BAPI_USER_PROFILES_ASSIGN = _rfc('BAPI_USER_PROFILES_ASSIGN')
BAPI_USER_ACTGROUPS_ASSIGN = _rfc('BAPI_USER_ACTGROUPS_ASSIGN')


RFC_READ_TABLE = _rfc('RFC_READ_TABLE')
BODS_RFC_READ_TABLE = _rfc('/BODS/RFC_READ_TABLE')
BODS_RFC_READ_TABLE2 = _rfc('/BODS/RFC_READ_TABLE2')
BODS_RFC_READ_TABLE_FIL = _rfc('/BODS/RFC_READ_TABLE_FIL')
BODS_RFC_STREAM_READ_TABLE = _rfc('/BODS/RFC_STREAM_READ_TABLE')
PM0_ABC_IBC_RFC_READ_TABLE = _rfc('/PM0/ABC_IBC_RFC_READ_TABLE')
SAPDS_RFC_READ_TABLE = _rfc('/SAPDS/RFC_READ_TABLE')
SAPDS_RFC_READ_TABLE2 = _rfc('/SAPDS/RFC_READ_TABLE2')
SAPDS_RFC_READ_TABLE_FILE = _rfc('/SAPDS/RFC_READ_TABLE_FILE')
SAPDS_RFC_STREAM_READ_TABLE = _rfc('/SAPDS/RFC_STREAM_READ_TABLE')
BBP_RFC_READ_TABLE = _rfc('BBP_RFC_READ_TABLE')
CNVCF_CCE_RFC_READ_TABLE = _rfc('CNVCF_CCE_RFC_READ_TABLE')
CNVCF_CCE_RFC_READ_TABLE_2 = _rfc('CNVCF_CCE_RFC_READ_TABLE_2')
CNVCF_CCE_RFC_READ_TABLE_TMP = _rfc('CNVCF_CCE_RFC_READ_TABLE_TMP')
CNVCF_CCE_RFC_READ_TABLE_UNI = _rfc('CNVCF_CCE_RFC_READ_TABLE_UNI')
CNV_CMIS_A_20_RFC_READ_TABLE = _rfc('CNV_CMIS_A_20_RFC_READ_TABLE')
EHPRC_MIGRATION_RFC_READ_TABLE = _rfc('EHPRC_MIGRATION_RFC_READ_TABLE')
RFC_READ_ALLOC_TABLE = _rfc('RFC_READ_ALLOC_TABLE')

RFC_CAN_READ_TABLE = frozenset(
    {
        RFC_READ_TABLE,
        BODS_RFC_READ_TABLE,
        BODS_RFC_READ_TABLE2,
        BODS_RFC_READ_TABLE_FIL,
        BODS_RFC_STREAM_READ_TABLE,
        PM0_ABC_IBC_RFC_READ_TABLE,
        SAPDS_RFC_READ_TABLE,
        SAPDS_RFC_READ_TABLE2,
        SAPDS_RFC_READ_TABLE_FILE,
        SAPDS_RFC_STREAM_READ_TABLE,
        BBP_RFC_READ_TABLE,
        CNVCF_CCE_RFC_READ_TABLE,
        CNVCF_CCE_RFC_READ_TABLE_2,
        CNVCF_CCE_RFC_READ_TABLE_TMP,
        CNVCF_CCE_RFC_READ_TABLE_UNI,
        CNV_CMIS_A_20_RFC_READ_TABLE,
        EHPRC_MIGRATION_RFC_READ_TABLE,
        RFC_READ_ALLOC_TABLE,
    }
)

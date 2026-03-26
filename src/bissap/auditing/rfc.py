from dataclasses import dataclass

from typing_extensions import override

from bissap.auditing.exploit_step import ExploitStep
from bissap.authorization import ACTVT, RFC_NAME, S_RFC, AuthorizationObject


@dataclass(frozen=True)
class Rfc(ExploitStep):
    authorization: AuthorizationObject

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
    def from_rfc_name(cls, rfc_name: str):
        return cls(S_RFC({RFC_NAME(rfc_name), ACTVT('16')}))

    @override
    def is_usable_by(self, profiles: set[str]):
        return self.authorization.profiles_has_authorization(profiles)


_rfc = Rfc.from_rfc_name


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

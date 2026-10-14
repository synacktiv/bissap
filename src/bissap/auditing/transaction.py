from dataclasses import dataclass

from typing_extensions import override

from bissap.auditing.exploit_step import ExploitStep
from bissap.authorization import S_TCODE, TCD, AuthorizationObject
from bissap.db import is_transaction_present


@dataclass(frozen=True)
class Transaction(ExploitStep):
    authorization: AuthorizationObject
    description: str | None = None

    def __post_init__(self):
        assert self.authorization.name == 'S_TCODE', (
            'Wrong authorization object. Expected S_TCODE'
        )
        assert len(self.authorization.fields) == 1, (
            'A S_TCODE transaction can only accept 1 field: TCD'
        )
        assert next(iter(self.authorization.fields)).name == 'TCD', (
            'Wrong authorization field. Expected TCD.'
        )

    @classmethod
    def from_tcode(cls, tcode: str, description: str | None = None):
        return cls(S_TCODE({TCD(tcode)}), description)

    @property
    def tcode(self):
        return next(iter(self.authorization.fields)).value

    @override
    def __repr__(self):
        return f'{self.tcode} ({self.description})'

    @override
    def is_usable_by(self, profiles: set[str]):
        return is_transaction_present(
            self.tcode
        ) and self.authorization.profiles_has_authorization(profiles)


_transaction = Transaction.from_tcode


# Known transactions
AL11 = _transaction('AL11', 'Directory listing')
CG3Z = _transaction('CG3Z', 'File upload')
DB02 = _transaction('DB02', 'Tables and Indexes Monitor')
PFCG = _transaction('PFCG', 'Maintain role using profile generator')
RSUDO = _transaction('RSUDO', 'Execution as Other User')
SA38 = _transaction('SA38', 'Execute ABAP program/report')
SE37 = _transaction('SE37', 'ABAP Function Modules')
SE16 = _transaction('SE16', 'Data Browser')
SE16H = _transaction('SE16H', 'General Table Display')
SE16N = _transaction('SE16N', 'General Table Display')
SE38 = _transaction('SE38', 'ABAP editor - create/edit/run ABAP program')
SM01 = _transaction('SM01', 'Lock/unlock transaction from execution')
SM04 = _transaction('SM04', 'User overview')
SM36 = _transaction('SM36', 'Simple job selection/scheduler')
SM37 = _transaction('SM37', 'Extended job selection/scheduler')
SM49 = _transaction('SM49', 'Execute external OS commands')
SM59 = _transaction('SM59', 'List Server trust')
SM69 = _transaction('SM69', 'Maintain external OS commands')
SQVI = _transaction('SQVI', 'QuickViewer')
ST04 = _transaction('ST04', 'Monitor Database Performance')
SU01 = _transaction('SU01', 'Create / Edit user')
SU01D = _transaction('SU01D', 'Display user details')
SU02 = _transaction('SU02', 'Create profil')
SU03 = _transaction('SU03', 'Create authorization')
SU10 = _transaction('SU10', 'Mass maintenance')
SU20 = _transaction('SU20', 'Maintain Authorization fields')
SU3 = _transaction('SU3', 'Maintain Users Own Data')
SUIM = _transaction('SUIM', 'User information')
CG3Y = _transaction('CG3Y', 'Download file')
SE11 = _transaction('SE11', 'ABAP Dictionnary Maintenance')
RZ10 = _transaction('RZ10', 'Maintain Profile Parameters')
RZ11 = _transaction('RZ11', 'Profile Parameter Maintenance')
LXE_MASTER = _transaction('LXE_MASTER', 'Translation Administration')
SXDA_TOOLS = _transaction('SXDA_TOOLS', 'DX Workbench: tools')
SM30 = _transaction('SM30', 'Maintain Table Views')
SM31 = _transaction('SM31', 'Maintain Table Views')

TRANSACTION_EXECUTE_JOB = {SM36, SM37, SM49}

# See https://www.aglea.com/en/blog/se16-in-sap for more examples of transactions that can read a table.
TRANSACTION_READ_TABLE = {SE16, SE16H, SE16N, SQVI}

TRANSACTION_WRITE_TABLE = {SE16N, SM30, SM31}

TRANSACTION_DOWNLOAD_FILE = {CG3Y, SXDA_TOOLS}

TRANSACTION_MAINTAIN_USER = {SU01, SU10}

JUICY_TRANSACTIONS = {
    SE38,
    SA38,
    CG3Z,
    CG3Y,
    SE16,
    # SE11,
    SM69,
    SM49,
    SU01,
    SU01D,
    SU03,
    SU10,
    # SU3, # SU3 is provided to a lot of users and does not seem very interesting. Very high noise.
    PFCG,
    SU20,
    SM01,
    SUIM,
    SM04,
    SM59,
    SA38,
    AL11,
    CG3Z,
    CG3Y,
    DB02,
    ST04,
    SM49,
    SM69,
    RSUDO,
}

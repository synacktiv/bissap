from bissap.auditing.rfc import RFC_CAN_READ_TABLE
from bissap.auditing.transaction import TRANSACTION_READ_TABLE
from bissap.authorization import all_profiles_with_access_to_table

SENSITIVE_TABLES = {
    # User master tables
    'USR02',
    'USH02',
    'USRPWDHISTORY',
    'USR01',
    'VUSR02_PWD',
    'USR40',
    'USR04',
    'USR10',
    'USR11',
    'USR12',
    # Bank/Payment tables
    'T012',
    'T012A',
    'T012C',
    'T012D',
    'T012E',
    'T012K',
    'T012O',
    'BNKA',
    'TIBAN',
}


def sensitive_tables_readable_by(profiles: set[str]) -> set[str]:
    """
    Return all interesting tables that can be read by any of the provided profiles.
    """

    # If the user cannot read any table, it cannot read any sensitive ones :P
    if not any(
        auth.is_usable_by(profiles)
        for auth in TRANSACTION_READ_TABLE | RFC_CAN_READ_TABLE
    ):
        return set()

    return {
        table_name
        for table_name in SENSITIVE_TABLES
        if len(all_profiles_with_access_to_table(table_name, 'ro') & profiles) > 0
    }

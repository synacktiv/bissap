from collections.abc import Iterable
from dataclasses import dataclass
from functools import lru_cache
import sqlite3
from typing import Literal

from bissap.globals import client
from bissap.db import select_all, select_first
from bissap.logging import get_logger
from bissap.profiles import get_profiles_of_role, get_profiles_of_user
from bissap.roles import get_role_with_profile
from bissap.users import all_users_name_with_profile

log = get_logger(__name__)


@dataclass(frozen=True)
class AuthorizationField:
    name: str
    value: str

    @staticmethod
    def template(name: str):
        def create_obj(value: str):
            return AuthorizationField(name, value)

        return create_obj


@dataclass(frozen=True)
class AuthorizationObject:
    name: str | None
    fields: frozenset[AuthorizationField]

    @staticmethod
    def template(name: str):
        def create_obj(value: Iterable[AuthorizationField]):
            return AuthorizationObject(name, frozenset(value))

        return create_obj

    def all_users_with_authorization(self):
        """
        Retrieve all users with a specific authorization, as specified by its object type and its fields.
        Also returns the profile granting this authorization.
        """

        matching_profiles = self.all_profiles_with_authorization()

        users = {
            (user, profile, get_role_with_profile(profile) or '')
            for profile in matching_profiles
            for user in all_users_name_with_profile(profile)
        }

        return users

    @lru_cache()
    def all_profiles_with_authorization(self):
        """
        Retrieve all profiles with a specific authorization, as specified by its object type and its fields.
        """

        def encode_name(name: str):
            """
            `name` may be a keyword (e.g. "TABLE" if searching for S_TABU_NAM authorizations).
            A keyword is not a valid table alias so it will crash if not handled.
            So we encode it by prepending something. There is no SQL keyword starting with `K_`.
            It is okay to not encode the name if we prepend/append something before using it as a table alias.
            """
            return f'K_{name}'

        def generate_prefixes(field: AuthorizationField):
            """
            Return a dictionnary of all prefixes of the field's value, with a * at the end.
            Also include '*' and the field value without a *
            """

            prefixes = {
                f'{field.name}_value': field.value,
            }
            for prefix_length in range(len(field.value) + 1):
                prefixes[f'{field.name}_value_{prefix_length}'] = (
                    field.value[:prefix_length] + '*'
                )
            return prefixes

        query = ''
        parameters: dict[str, str] = {}

        fields = list(self.fields)
        first_field = fields.pop()

        query += f'SELECT ROOTPROFN FROM PROFILE_AUTHS {encode_name(first_field.name)}'

        # Filter common parameters
        query += ' WHERE MANDT=:mandt'
        parameters['mandt'] = client()

        if self.name is not None:
            query += ' AND OBJCT=:objct'
            parameters['objct'] = self.name

        # Treat the first field as a special case, to reduce the number of queries.
        first_field_prefixes = generate_prefixes(first_field)
        parameters[f'{first_field.name}_field'] = first_field.name
        parameters |= first_field_prefixes

        query += (
            f' AND {encode_name(first_field.name)}.FIELD = :{first_field.name}_field'
            + f' AND {encode_name(first_field.name)}.VON IN ({", ".join([":" + arg for arg in first_field_prefixes])})'
        )
        # For each field, we use one JOIN to filter for it
        for field in fields:
            t1 = encode_name(first_field.name)
            t2 = encode_name(field.name)

            # Mimic the condition used by a JOIN.
            keys = {'MANDT', 'OBJCT', 'AUTH', 'ROOTPROFN'}
            subquery = f'SELECT 1 FROM PROFILE_AUTHS {t2} WHERE ' + ' AND '.join(
                f'{t1}.{key} = {t2}.{key}' for key in keys
            )

            prefixes = generate_prefixes(field)
            parameters[f'{field.name}_field'] = field.name
            parameters |= prefixes

            subquery += (
                f' AND {encode_name(field.name)}.FIELD = :{field.name}_field'
                + f' AND {encode_name(field.name)}.VON IN ({", ".join([":" + arg for arg in prefixes])})'
            )

            query += f' AND EXISTS({subquery})'

        result: list[tuple[str]] = select_all(query, parameters)

        return {prof for (prof,) in result}

    def user_has_authorization(self, bname: str):
        """
        Check whether the provided user can satisfy the authorization described by `self`.
        """
        return self.profiles_has_authorization(get_profiles_of_user(bname))

    def role_has_authorization(self, role_name: str):
        """
        Check whether the provided role can satisfy the authorization described by `self`.
        """
        return self.profiles_has_authorization(get_profiles_of_role(role_name))

    def profiles_has_authorization(self, profiles: Iterable[str]):
        """
        Check whether any of the profiles provided can satisfy the authorization described by `self`.
        """
        return len(self.all_profiles_with_authorization().intersection(profiles)) > 0


@lru_cache()
def all_profiles_with_access_to_table(
    table_name: str, wanted_access: Literal['ro', 'rw']
) -> set[str]:
    match wanted_access:
        case 'ro':
            actvt = '03'
        case 'rw':
            # TODO: 02 means "change". It does not garantee a read access too.
            actvt = '02'

    try:
        res: str | None = select_first(
            'SELECT CCLASS FROM TDDAT WHERE TABNAME=?',
            (table_name,),
        )
        if res is None:
            # Table does not exists, no users can read it.
            return set()
        table_security_group = res[0]
    except sqlite3.OperationalError:
        log.warning(
            'Table TDDAT is missing. Access checks granted with S_TABU_DIS will not be precise enough.'
        )
        # If we cannot find the table's security group, we at least filter for users with wildcard access to tables.
        table_security_group = '*'

    access_by_name = S_TABU_NAM({TABLE(table_name), ACTVT(actvt)})
    profiles_by_name = access_by_name.all_profiles_with_authorization()

    access_by_class = S_TABU_DIS({DICBERCLS(table_security_group), ACTVT(actvt)})
    profiles_by_class = access_by_class.all_profiles_with_authorization()

    # If either of the checks succeeds, access is granted.
    return profiles_by_name | profiles_by_class


_field = AuthorizationField.template

ACTVT = _field('ACTVT')
OBJTYPE = _field('OBJTYPE')
OBJNAME = _field('OBJNAME')
DEVCLASS = _field('DEVCLASS')
PROGRAM = _field('PROGRAM')
CFUNCNAME = _field('CFUNCNAME')
COMMAND = _field('COMMAND')
TCD = _field('TCD')
TABLE = _field('TABLE')
DICBERCLS = _field('DICBERCLS')
RFC_NAME = _field('RFC_NAME')
RFC_TYPE = _field('RFC_TYPE')
FILENAME = _field('FILENAME')

_object = AuthorizationObject.template

S_DEVELOP = _object('S_DEVELOP')
S_C_FUNCT = _object('S_C_FUNCT')
S_LOG_COM = _object('S_LOG_COM')
S_RZL_ADM = _object('S_RZL_ADM')
S_TCODE = _object('S_TCODE')
S_TABU_NAM = _object('S_TABU_NAM')
S_TABU_DIS = _object('S_TABU_DIS')
S_RFC = _object('S_RFC')
S_DATASET = _object('S_DATASET')

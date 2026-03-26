# bissap

This tool allows for a rapid analysis of an SAP database to identify users or roles configured with dangerous permissions or combination of permissions. It is similar to **Bloodhound** for Active Directory.

---

## Installation

You can use `pipx` :

```
$ pipx install git+https://github.com/synacktiv/bissap.git
```

Or, using `pip` :

```console
$ git clone https://github.com/synacktiv/bissap
$ python3 -m venv .venv && . .venv/bin/activate # Optional: Install in a venv
$ pip install .
```

Or, if you prefer using Debian packages:

```console
# apt install python3-click python3-colorlog python3-sqlalchemy python3-frozendict python3-rich python3-openpyxl python3-typing-extensions
$ PYTHONPATH=src/ python3 src/bissap/commands/__init__.py
```

---

## Program Workflow

bissap works in 3 steps:

1. **Collecting**: The data is collected from the SAP system's database. This data is either collected by connecting to the database directly or by dumping it from the GUI.
2. **Importing**: This collected data is imported to a local SQLite database.
3. **Analyzing**: From this database, queries can be executed and you can perform an **automated audit** to quickly identify users with dangerous access levels. **Manual searching** is also possible to look for undocumented or environment-specific attack scenarios.

---

# Examples

## Generating the Data Collection Script

```console
$ bissap collect -t sybase
Copy this command, set the appropriate variables and execute the command. Copy the file `/tmp/dump_bissap.csv` to your host.
Call bissap -d DATABASE.sqlite import -i dump_bissap.csv to continue.
isql -X -w9999999999 -s'|' -U$USER -P$PASSWORD -H$HOST -S$SYSTEM -o /tmp/dump_bissap.csv << EOF
...
GO
EOF
$ ... # Manually execute the script
$ scp host:/tmp/dump_bissap.csv npl.csv
```

## Importing Collected Data and Displaying Debug Logs

```console
$ LOG_LEVEL=debug bissap -d npl.sqlite import -i npl.csv
INFO:src.file_import:Importing the database. Be patient, it may take 5 minutes or more.
...
DEBUG:src.file_import:Denormalizing the database.
```

## Automated Audit of Client 001

```console
$ bissap -d npl.sqlite -m 001 audit
BWDEVELOPER is vulnerable to 9 RCE(s).
BWDEVELOPER can read 17 sensitive tables.
BWDEVELOPER can execute 20 "juicy" transactions. (SE16, RSUDO, SM49, SE38, SE11, SM69, SU10, SU01, PFCG, SA38, SU01D, SM59, SU03, SU20, AL11, ST04, SUIM, SM01, DB02, SM04)
...
TEST2 can execute 1 "juicy" transactions. (SE11)
```

## Detailed Audit of a Specific User

```console
$ bissap -d npl.sqlite -m 1 audit -u 'SAP*'
SAP* is vulnerable to 9 RCE(s).
# CG3Z+SM36
> Go to CG3Z (File upload)
> Then create a new external command or edit an existing one
> Then set and save the OS command that you want to run
> Finally execute it using SM36 (Simple job selection/scheduler)
...
```

## Role Audit

```console
$ bissap -d npl.sqlite -m 1 audit --roles
ZDEVELOPER is vulnerable to 1 RCE(s).
ZDEVELOPER can execute 3 "juicy" transactions. (SU01, PFCG, SE38)
```

## Audit of a User's Roles

```console
$ bissap -d npl.sqlite -m 1 audit --roles -u DEVELOPER
ZDEVELOPER is vulnerable to 1 RCE(s).
ZDEVELOPER can execute 3 "juicy" transactions. (SU01, PFCG, SE38)
```
*(Since the user `DEVELOPER` has only one role, which is also the only vulnerable role, it is normal for the output to be the same.)*

## Detailed Audit of a Specific Role

```console
$ bissap -d npl.sqlite -m 1 audit -r ZDEVELOPER
ZDEVELOPER is vulnerable to 1 RCE(s).
# SE38
 Go to SE38 (ABAP editor - create/edit/run ABAP program)
> Create a new ABAP program (but you will need a developer key if you don't have a "developer" account)
> Then execute it using SE38.
...
```

## List Users Authorized to Execute Transaction `SM16`

```console
$ bissap -d npl.sqlite -m 1 users by-auth -t SM16
TEST
SAP*
BWDEVELOPER
DDIC
DEVELOPER
```

## List Profiles Assigned to User `DDIC`

```console
$ bissap -d npl.sqlite -m 1 profiles of-user DDIC
SAP_ALL
S_A.SYSTEM
```

## List Users with the `SAP_ALL` Profile

```console
$ bissap -d npl.sqlite -m 1 users by-profile -p SAP_ALL
BWDEVELOPER
DDIC
DEVELOPER
SAP*
TEST
```
# About
**Work In Progress**

Command line python scripts for G Suite to automate specific operations with Drive, Gmail etc.
Used to generate invoices and reports, save them as PDF, create Gmail drafts with PDFs and so on.
Contains only commands needed in CRM.

Drive API v3 used.

# Usage
## Commands
Commands use [IDs of Drive files](https://developers.google.com/drive/api/v3/about-files#file_ids).

```
./drive.py --help
usage: drive.py [-h] [--debug] [--cd CD] [--name NAME] [--ls] [--mkdir MKDIR]
                [--cp CP]

Script to automate specific operations with G Suite Drive.

optional arguments:
  -h, --help     show this help message and exit
  --debug        enable debug
  --cd CD        operate in folder specified by google drive ID CD
  --name NAME    give new file name NAME, if required by command
  --ls           returns ID<space>name of files, optionally with --cd
  --mkdir MKDIR  create folder named MKDIR, only if it does not exist yet,
                 returns ID of created or found folder, use always with --cd
  --cp CP        copy file referenced by google drive ID CP only if it does
                 not exist yet, returns ID of created file if created, use
                 always with --cd and --name
```
## Required Projects and APIs
### Developers Project
Projects are managed on [Developers Console](https://console.developers.google.com/).
- Create project.
- Enable APIs for the project:
  - Apps Script API
  - Google Drive API
  - Google Sheets API

Scripts are going to use Service Account auth to access G Suite.

From the [manual](https://developers.google.com/api-client-library/python/auth/service-accounts) follow the steps to create Service Account.

Create JSON secrets file for the Service Account and save it in a safe place.

Note the Service Account email - you will need it.

You don't need to Enable G Suite Domain-wide Delegation - you can use Service Account's email @...iam.gserviceaccount.com to share access to specific folder in Drive etc with Service Account.

## Required envs
- SA_SECRETS_FILE - path to the Service Account JSON secrets.

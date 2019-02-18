# About
G Suite scripts to automate specific operations with Drive, Gmail etc. Used to generate invoices and reports, save them as PDF, create Gmail drafts with PDFs and so on.

# Usage
## Commands
Commands use [IDs of Drive files](https://developers.google.com/drive/api/v3/about-files#file_ids).

- `drive.py --ls` - List files, optionaly in folder specified with `--cd ID`.
- `drive.py --mkdir "Some Folder Name"` - Create folder inside other folder specified with `--cd ID`.
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

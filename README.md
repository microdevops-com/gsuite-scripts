# About
**Work In Progress**

Command line python scripts for G Suite to automate operations with Drive, Docs, Sheets and Gmail.
Used to generate invoices and reports (actually, any kind of documents, it depends only on the template document used), save them as PDF, create Gmail drafts with PDFs, add data to sheets.

API versions used:
  - [Drive API v3](https://developers.google.com/drive/api/v3/quickstart/python)
  - [Docs API v1](https://developers.google.com/docs/api/quickstart/python)
  - [Sheets API v4](https://developers.google.com/sheets/api/quickstart/python)
  - [Gmail API v1](https://developers.google.com/gmail/api/quickstart/python)

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
## Required Projects, APIs, permissions
### Developers Project
Go to [Developers Console](https://console.developers.google.com/), authorize with your G Suite admin and create new project within your organization.

Go to API Library and enable the following APIs for the project:
  - Google Drive API
  - Google Docs API
  - Google Sheets API
  - Gmail API

Scripts are going to use Service Account auth to access G Suite.

From the [manual](https://developers.google.com/api-client-library/python/auth/service-accounts) follow the steps to create Service Account.

Create JSON secrets file for the Service Account and save it in a safe place accessible to scripts.

Note the Service Account email (...@...iam.gserviceaccount.com) - you will need it.

### Drive
Create folder you want to manipulate with scripts.

Share access to the folder with Service Account's email.

**Caution**: if you delete service account, all files created by service account will also be deleted. Transfer files ownership beforehand.

### Gmail
If you need to create drafts within Gmail with scripts, you need to enable Domain-wide delegation for Service Account.
It is not required for Drive, but there is no other way to delegate mailbox control to Service Account for Gmail.
If you enable it for Gmail - your code will be able to access **ALL** email mailboxes of your organization - you cannot select specific mailboxes (like you can share only specific folders or files in Drive with service account).

So it is better to limit with Scopes Domain-wide access only to Gmail, and not to allow Drive access, because it is not needed.

Go to Project API Credentials Dashboard.

Choose OAuth Consent Screen tab.

Set Application Name - it is required to be filled, switch to Internal application usage.

Enable [Domain-wide delegation](https://developers.google.com/admin-sdk/directory/v1/guides/delegation):

Edit Service Account settings in Service Accounts menu.

Check Enable G Suite Domain-wide Delegation.

Note Client ID (all digits) of Service Account after enabling.

Go to G Suite Admin -> Security -> Advanced -> Manage API Client Access.

In the Client name field enter the service account's Client ID.

Set Scopes for Gmail:
```
https://mail.google.com/,https://www.googleapis.com/auth/gmail.compose,https://www.googleapis.com/auth/gmail.metadata,https://www.googleapis.com/auth/gmail.readonly,https://www.googleapis.com/auth/gmail.send
```
## Required envs
- SA_SECRETS_FILE - path to the Service Account JSON secrets.

# Notes on Script API
Script API and JS Scripts are **NOT** used - people often use those mechanisms to manipulate data within docs and sheets, but there are native API calls for docs and sheets that do the very same.
Also, Script API [cannot be used with service accounts](https://issuetracker.google.com/issues/36763096), which is the simpliest OAuth way.

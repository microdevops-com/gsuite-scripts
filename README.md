# About
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
usage: drive.py [-h] [--debug]
                (--ls ID | --rm ID | --mkdir ID NAME | --cp ID CD NAME | --pdf ID NAME | --download ID NAME | --upload FILE CD NAME)

Script to automate specific operations with G Suite Drive.

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug
  --ls ID               returns id<space>name<mimeType> of files available in
                        folder ID, use ID = ALL to list all available files
  --rm ID               delete file ID (folders are also files in drive)
  --mkdir ID NAME       create folder NAME within folder ID, only if NAME does
                        not exist yet, returns ID of created or found folder
  --cp ID CD NAME       copy source file ID to folder CD with NAME, only if it
                        does not exist yet, returns ID of created file if
                        created
  --pdf ID NAME         download file ID as pdf file NAME
  --download ID NAME    download file ID as file NAME
  --upload FILE CD NAME
                        upload local FILE as NAME to google drive folder CD,
                        only if it does not exist yet, returns ID of created
                        file if created
```
```
usage: docs.py [-h] [--debug]
               (--get-as-json ID | --replace-all-text ID JSON | --insert-table-rows ID TABLE_NUM BELOW_ROW_NUMBER JSON | --delete-table-row ID TABLE_NUM ROW_NUMBER)

Script to automate specific operations with G Suite Docs.

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug
  --get-as-json ID      get google drive doc ID as json
  --replace-all-text ID JSON
                        replace all text templates defined by JSON (e.g.
                        '{"__KEY1__": "Value 1", "__KEY2__": "Value 2"}')
                        within google drive doc ID
  --insert-table-rows ID TABLE_NUM BELOW_ROW_NUMBER JSON
                        insert rows defined by JSON (e.g. '[["Cell 1-1", "Cell
                        1-2"], ["Cell 2-1", "Cell 2-2"]]') into TABLE_NUM
                        (table, row count starts from 1) below row number
                        BELOW_ROW_NUMBER within google drive doc ID
  --delete-table-row ID TABLE_NUM ROW_NUMBER
                        delete row ROW_NUMBER from TABLE_NUM (table, row count
                        starts from 1) within google drive doc ID
```
```
usage: sheets.py [-h] [--debug]
                 (--get-as-json ID SHEET RANGE DIMENSION RENDER DATETIME_RENDER | --append-data ID SHEET RANGE DIMENSION JSON)

Script to automate specific operations with G Suite Docs.

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug
  --get-as-json ID SHEET RANGE DIMENSION RENDER DATETIME_RENDER
                        get google drive spreadsheet ID range RANGE on sheet
                        SHEET as json, use DIMENSION = 'ROWS' or 'COLUMNS',
                        RENDER = 'FORMATTED_VALUE' or 'UNFORMATTED_VALUE' or
                        'FORMULA', DATETIME_RENDER = 'SERIAL_NUMBER' or
                        'FORMATTED_STRING'
  --append-data ID SHEET RANGE DIMENSION JSON
                        append table defined by RANGE (e.g. A:B) within google
                        drive spreadsheet ID on sheet SHEET, data (one or
                        multiple rows or columns) is provided with JSON (e.g.
                        [["Cell 1 1", "Cell 1 2"], ["Cell 2 1", "Cell 2 2"]]),
                        use DIMENSION = 'ROWS' or 'COLUMNS'
```
```
usage: gmail.py [-h] [--debug]
                (--create-draft USER FROM TO CC BCC SUBJECT TEXT ATTACH | --send-draft USER DRAFT_ID | --list-messages USER)

Script to automate specific operations with Gmail.

optional arguments:
  -h, --help            show this help message and exit
  --debug               enable debug
  --create-draft USER FROM TO CC BCC SUBJECT TEXT ATTACH
                        create draft inside USER gmail, from email FROM to
                        email(s) TO, CC, BCC with SUBJECT and TEXT, and attach
                        local files listed with json list ATTACH, e.g.
                        --create-draft me@example.com '"Me Myself"
                        <me@example.com>' '"Client 1" <client1@acme.com>,
                        "Client 2" <client2@acme.com>' '"Someone Other"
                        cc@acme.com' 'bcc@acme.com' 'Subject may contain UTF -
                        перевірка チェックする' 'Message may contain UTF and
                        new\nlines\nперевірка\nチェックする' '["a.pdf", "b.pdf"]'
  --send-draft USER DRAFT_ID
                        send draft DRAFT_ID inside USER gmail
  --list-messages USER  list messages available to gmail USER
```
## Required envs for commands
- `SA_SECRETS_FILE` - path to the Service Account JSON secrets.
- `LOG_DIR` - path to put logs into.

## Functions
Functions could be used in other scripts:
```
from gsuite_scripts import *
response = docs_get_as_json(SA_SECRETS_FILE, doc_id)
response = docs_replace_all_text(SA_SECRETS_FILE, doc_id, json_str)
response_new_row, response_values = docs_insert_table_row(SA_SECRETS_FILE, doc_id, table_num, below_row_number, json_str)
items = drive_ls(SA_SECRETS_FILE, cd_folder)
response = drive_rm(SA_SECRETS_FILE, file_id)
response = drive_mkdir(SA_SECRETS_FILE, in_id, folder_name)
response = drive_cp(SA_SECRETS_FILE, source_id, cd_id, file_name)
response = drive_pdf(SA_SECRETS_FILE, file_id, file_name)
response = drive_upload(SA_SECRETS_FILE, file_local, cd_id, file_name)
response = sheets_get_as_json(SA_SECRETS_FILE, spreadsheet_id, sheet_id, range_id, dimension, render, datetime_render)
response = sheets_append_data(SA_SECRETS_FILE, spreadsheet_id, sheet_id, range_id, dimension, json_str)
draft_id, draft_message = gmail_create_draft(SA_SECRETS_FILE, gmail_user, message_from, message_to, message_cc, message_bcc, message_subject, message_text, attach_str)
response = gmail_list_messages(SA_SECRETS_FILE, gmail_user)
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
# Notes on Script API
Script API and JS Scripts are **NOT** used - people often use those mechanisms to manipulate data within docs and sheets, but there are native API calls for docs and sheets that do the very same.
Also, Script API [cannot be used with service accounts](https://issuetracker.google.com/issues/36763096), which is the simpliest OAuth way.

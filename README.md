# About
G Suite scripts to automate specific operations with Drive, Gmail etc. Used to generate invoices and reports, save them as PDF, create Gmail drafts with PDFs and so on.

# Usage
## Required Projects and APIs
### Developers Project
Projects are managed on https://console.developers.google.com/ .
- Create project.
- Enable APIs for the project:
  - Apps Script API
  - Google Drive API
  - Google Sheets API

Scripts are going to use Service Account auth to access G Suite.

From the manual https://developers.google.com/api-client-library/python/auth/service-accounts follow the steps to create Service Account.

Create JSON key file for the Service Account and save it in a safe place.

Note the Service Account email - you will need it.

You don't need to Enable G Suite Domain-wide Delegation - you can use Service Accouna'st email @...iam.gserviceaccount.com to share access to specific folder in Drive etc with Service Account.

## Required envs


# -*- coding: utf-8 -*-
from sysadmws_common import *
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account
import io
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import mimetypes
from email import encoders
import string
from retrying import retry

# Constants
GSUITE_RETRIES = 3
DOCS_SCOPES = ['https://www.googleapis.com/auth/documents']
DRIVE_SCOPES = ['https://www.googleapis.com/auth/drive']
SHEETS_SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
GMAIL_SCOPES = [
    'https://mail.google.com/',
    'https://www.googleapis.com/auth/gmail.compose',
    #'https://www.googleapis.com/auth/gmail.metadata', with this scope you cannot get messages
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send'
]

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def docs_get_as_json(sa_secrets_file, doc_id):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DOCS_SCOPES)
        docs_service = build('docs', 'v1', credentials=credentials)

        response = docs_service.documents().get(documentId=doc_id).execute()
    
        return response
    
    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def docs_replace_all_text(sa_secrets_file, doc_id, json_str):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DOCS_SCOPES)
        docs_service = build('docs', 'v1', credentials=credentials)

        json_dict = json.loads(json_str)

        requests = []

        for template in json_dict:

            requests = requests + [
                {   
                    'replaceAllText': {
                        'containsText': {
                            'text': template,
                            'matchCase':  'true'
                        },
                        'replaceText': json_dict[template]
                    }
                }
            ]

        response = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        return response
    
    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def docs_insert_table_rows(sa_secrets_file, doc_id, table_num, below_row_number, json_str):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DOCS_SCOPES)
        docs_service = build('docs', 'v1', credentials=credentials)

        json_list = json.loads(json_str)
        below_row_index = int(below_row_number) - 1
        table_num = int(table_num)

        # Get table index

        response = docs_service.documents().get(documentId=doc_id).execute()

        content = response['body']['content']
        table_n = 0
        table_index = None

        for element in content:

            if "table" in element:

                table_n += 1
                if table_n == table_num:

                    # Save table startIndex
                    table_index = element['startIndex']

                    # Save endIndex of the row below which we will insert
                    # We can calc new row first cell startIndex by this endIndex

                    table = element['table']
                    rows = table['tableRows']
                    row_n = 0
                    row_end_index = None

                    # Check if requested below_row_num is out of table rows
                    if int(below_row_number) > len(rows):
                        raise ValueError("Table {0} has less than {1} rows ({2} actually)".format(table_num, below_row_number, len(rows)))

                    for row in rows: # For some reason row[x] doesn't work, so just iterate

                        row_n += 1
                        if row_n == int(below_row_number):

                            row_end_index = int(row['endIndex'])

                    if row_end_index is None:
                        raise ValueError("Row {0} index for table {1} not found".format(below_row_number, table_num))

        if table_index is None:
            raise ValueError("Table index for TABLE_NUM = {0} not found".format(table_num))

        # Iterate on first dimension of json_list - rows - starting from last row
        # As per https://developers.google.com/docs/api/how-tos/best-practices data should be filled backwards
        # Populate requests list in iterations
        
        requests = []
        json_list.reverse()
        for list_row in json_list:

            # Insert new row
            requests = requests + [
                {
                    'insertTableRow': {
                        'tableCellLocation': {
                            'tableStartLocation': {
                                'index': table_index
                            },
                            'rowIndex': below_row_index,
                            'columnIndex': 0
                        },
                        'insertBelow': 'true'
                    }
                }
            ]

            # Fill row values, also backwards

            list_n = 0
            list_row.reverse()

            for list_cell in list_row:

                requests = requests + [
                    {
                        'insertText': {
                            'location': {
                                'index': row_end_index + ( 2 * (len(list_row) - list_n) )
                            },
                            'text': list_cell
                        }
                    }
                ]

                list_n += 1

        response = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        return response

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def docs_delete_table_row(sa_secrets_file, doc_id, table_num, row_number):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DOCS_SCOPES)
        docs_service = build('docs', 'v1', credentials=credentials)

        row_index = int(row_number) - 1
        table_num = int(table_num)

        # Get table index

        response = docs_service.documents().get(documentId=doc_id).execute()

        content = response['body']['content']
        table_n = 0
        table_index = None

        for element in content:

            if "table" in element:

                table_n += 1
                if table_n == table_num:

                    # Save table startIndex
                    table_index = element['startIndex']

                    # Save endIndex of the row which we will delete
                    # We can calc new row first cell startIndex by this endIndex

                    table = element['table']
                    rows = table['tableRows']
                    row_n = 0
                    row_end_index = None

                    # Check if requested row_num is out of table rows
                    if int(row_number) > len(rows):
                        raise ValueError("Table {0} has less than {1} rows ({2} actually)".format(table_num, row_number, len(rows)))

                    for row in rows: # For some reason row[x] doesn't work, so just iterate

                        row_n += 1
                        if row_n == int(row_number):

                            row_end_index = int(row['endIndex'])

                    if row_end_index is None:
                        raise ValueError("Row {0} index for table {1} not found".format(row_number, table_num))

        if table_index is None:
            raise ValueError("Table index for TABLE_NUM = {0} not found".format(table_num))

        # Insert new row

        requests = [
            {
                'deleteTableRow': {
                    'tableCellLocation': {
                        'tableStartLocation': {
                            'index': table_index
                        },
                        'rowIndex': row_index,
                        'columnIndex': 0
                    }
                }
            }
        ]

        response_delete_row = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()

        return response_delete_row

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_ls(sa_secrets_file, cd_folder, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        page_token = None
        return_items = []

        while True:

            if cd_folder == "ALL":
                q = ""
            else:
                q = "'{0}' in parents".format(cd_folder)

            # Try to list files, suppress errors
            try:
                response = drive_service.files().list(pageSize=100, fields="nextPageToken, files(id, name, mimeType)", pageToken=page_token, q=q).execute()
                items = response.get('files', [])
                page_token = response.get('nextPageToken', None)
            except:
                raise 
            
            for item in items:
                return_items.append({'id': item['id'], 'name': item['name'], 'mimeType': item['mimeType']})

            if page_token is None:
                break

        return return_items

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_ls_perms(sa_secrets_file, ls_perms_id, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        page_token = None
        return_items = []

        while True:

            # Try to list files, suppress errors
            try:
                response = drive_service.permissions().list(pageSize=100, fields="nextPageToken, permissions(id, type, emailAddress, role)", pageToken=page_token, fileId=ls_perms_id).execute()
                items = response.get('permissions', [])
                page_token = response.get('nextPageToken', None)
            except:
                raise

            for item in items:
                return_items.append({'id': item['id'], 'type': item['type'], 'emailAddress': item['emailAddress'], 'role': item['role']})

            if page_token is None:
                break

        return return_items

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_rm(sa_secrets_file, file_id, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        return drive_service.files().delete(fileId=file_id).execute()

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_mkdir(sa_secrets_file, in_id, folder_name, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            print(drive_user)
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        # Query if the same file already exists
        q = "'{0}' in parents and name = '{1}'".format(in_id, folder_name)

        # Get only one page with 1 result
        response = drive_service.files().list(pageSize=1, fields="files(id, name)", q=q).execute()
        items = response.get('files', [])

        if not items:

            body = {
                'name': folder_name,
                'mimeType': "application/vnd.google-apps.folder",
                'parents': [in_id]
            }

            folder = drive_service.files().create(body=body).execute()

            return folder['id']

        else:

            return items[0]['id']

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_cp(sa_secrets_file, source_id, cd_id, file_name, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        # Query if the same file already exists
        q = "'{0}' in parents and name = '{1}'".format(cd_id, file_name)

        # Get only one page with 1 result
        response = drive_service.files().list(pageSize=1, fields="files(id, name)", q=q).execute()
        items = response.get('files', [])

        if not items:

            body = {
                'name': file_name,
                'parents': [cd_id]
            }

            new_file = drive_service.files().copy(fileId=source_id, body=body).execute()

            return new_file['id']

        else:

            return None

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_pdf(sa_secrets_file, file_id, file_name, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        request = drive_service.files().export_media(fileId=file_id, mimeType='application/pdf')

        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.close()
        return status.progress() * 100

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_download(sa_secrets_file, file_id, file_name, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        request = drive_service.files().get_media(fileId=file_id)

        fh = io.FileIO(file_name, "wb")
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        fh.close()
        return status.progress() * 100

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def drive_upload(sa_secrets_file, file_local, cd_id, file_name, drive_user=None):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=DRIVE_SCOPES)
        if drive_user is None:
            drive_service = build('drive', 'v3', credentials=credentials)
        else:
            delegated_credentials = credentials.with_subject(drive_user)
            drive_service = build('drive', 'v3', credentials=delegated_credentials)

        # Query if the same file already exists
        q = "'{0}' in parents and name = '{1}'".format(cd_id, file_name)

        # Get only one page with 1 result
        response = drive_service.files().list(pageSize=1, fields="files(id, name)", q=q).execute()
        items = response.get('files', [])

        if not items:

            body = {
                'name': file_name,
                'parents': [cd_id]
            }

            media = MediaFileUpload(file_local)
            new_file = drive_service.files().create(body=body, media_body=media, fields='id').execute()

            return new_file['id']
        
        else:

            return None

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def sheets_get_as_json(sa_secrets_file, spreadsheet_id, sheet_id, range_id, dimension, render, datetime_render):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=SHEETS_SCOPES)
        sheets_service = build('sheets', 'v4', credentials=credentials)

        sheet = sheets_service.spreadsheets()
        result = sheet.values().get(spreadsheetId=spreadsheet_id, range="{0}!{1}".format(sheet_id, range_id), majorDimension=dimension, valueRenderOption=render, dateTimeRenderOption=datetime_render).execute()
        values = result.get('values', [])

        # Calculate range column size

        num = 0
        for c in range_id.split(":")[0]:
            if c in string.ascii_letters:
                num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        left_column = num
        
        num = 0
        for c in range_id.split(":")[1]:
            if c in string.ascii_letters:
                num = num * 26 + (ord(c.upper()) - ord('A')) + 1
        right_column = num

        range_size = right_column - left_column + 1

        # Sheets api omits row tail if its values are empty
        # Rebuild values filling tails with empty strings truncated tails

        new_values = []
        for row in values:
            new_row = []
            for col_num in range(range_size):
                try:
                    new_row.append(row[col_num])
                except IndexError:
                    new_row.append("")
            new_values.append(new_row)

        return new_values

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def sheets_append_data(sa_secrets_file, spreadsheet_id, sheet_id, range_id, dimension, json_str):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=SHEETS_SCOPES)
        sheets_service = build('sheets', 'v4', credentials=credentials)

        json_dict = json.loads(json_str)
        
        request = {
            "majorDimension": dimension,
            "values": json_dict
        }

        response = sheets_service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, range="{0}!{1}".format(sheet_id, range_id), valueInputOption="USER_ENTERED", insertDataOption="INSERT_ROWS", body=request).execute()

        return response

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def gmail_create_draft(sa_secrets_file, gmail_user, message_from, message_to, message_cc, message_bcc, message_subject, message_text, attach_str):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=GMAIL_SCOPES)
        delegated_credentials = credentials.with_subject(gmail_user)
        gmail_service = build('gmail', 'v1', credentials=delegated_credentials)

        message_text_new_lines = message_text.replace('\\n', '\n')
        attach_list = json.loads(attach_str)

        message = MIMEMultipart()
        message['From'] = message_from
        message['To'] = message_to
        message['Cc'] = message_cc
        message['Bcc'] = message_bcc
        message['Subject'] = message_subject

        message.attach(MIMEText(message_text_new_lines, "plain"))

        for file_name in attach_list:

            with open(file_name, "rb") as attachment:

                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())

            encoders.encode_base64(part)
            part.add_header("Content-Disposition", "attachment", filename=os.path.basename(file_name))
            message.attach(part)

        b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
        b64_string = b64_bytes.decode()
        message_body = {'raw': b64_string}
        message = {'message': message_body}
        draft = gmail_service.users().drafts().create(userId='me', body=message).execute()

        return draft['id'], draft['message']

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def gmail_list_messages(sa_secrets_file, gmail_user):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=GMAIL_SCOPES)
        delegated_credentials = credentials.with_subject(gmail_user)
        gmail_service = build('gmail', 'v1', credentials=delegated_credentials)

        response = gmail_service.users().messages().list(userId=gmail_user).execute()
        return_list = []

        if 'messages' in response:

            for msg in response['messages']:

                message = gmail_service.users().messages().get(userId=gmail_user, id=msg['id'], format='raw').execute()
                return_list.append(msg)
                return_list.append(message['snippet'])
            
        return return_list

    except:
        raise

@retry(stop_max_attempt_number=GSUITE_RETRIES)
def gmail_send_draft(sa_secrets_file, gmail_user, draft_id):

    try:

        credentials = service_account.Credentials.from_service_account_file(sa_secrets_file, scopes=GMAIL_SCOPES)
        delegated_credentials = credentials.with_subject(gmail_user)
        gmail_service = build('gmail', 'v1', credentials=delegated_credentials)

        body = {'id': draft_id}
        message = gmail_service.users().drafts().send(userId='me', body=body).execute()

        return message

    except:
        raise

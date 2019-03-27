#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *

# Import ext libs
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account
import io
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload

# Constants
LOGO="G Suite Scripts / Drive"
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "/opt/sysadmws/gsuite-scripts/log"
LOG_FILE = "drive.log"
SCOPES = ['https://www.googleapis.com/auth/drive']
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main

if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with G Suite Drive.')
    parser.add_argument("--debug",              dest="debug",               help="enable debug",                        action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    ls_help = "returns id<space>name of files available in folder ID, use ID = ALL to list all available files"
    group.add_argument("--ls",                  dest="ls",                  help=ls_help,                               nargs=1,    metavar=("ID"))
    rm_help = "delete file ID (folders are also files in drive)"
    group.add_argument("--rm",                  dest="rm",                  help=rm_help,                               nargs=1,    metavar=("ID"))
    mkdir_help = "create folder NAME within folder ID, only if NAME does not exist yet, returns ID of created or found folder"
    group.add_argument("--mkdir",               dest="mkdir",               help=mkdir_help,                            nargs=2,    metavar=("ID", "NAME"))
    cp_help = "copy source file ID to folder CD with NAME, only if it does not exist yet, returns ID of created file if created"
    group.add_argument("--cp",                  dest="cp",                  help=cp_help,                               nargs=3,    metavar=("ID", "CD", "NAME"))
    group.add_argument("--pdf",                 dest="pdf",                 help="download file ID as pdf file NAME",   nargs=2,    metavar=("ID", "NAME"))
    upload_help = "upload local FILE as NAME to google drive folder CD, only if it does not exist yet, returns ID of created file if created"
    group.add_argument("--upload",              dest="upload",              help=upload_help,                           nargs=3,    metavar=("FILE", "CD", "NAME"))
    args = parser.parse_args()

    # Set logger and console debug
    if args.debug:
        logger = set_logger(logging.DEBUG, LOG_DIR, LOG_FILE)
    else:
        logger = set_logger(logging.ERROR, LOG_DIR, LOG_FILE)

    # Catch exception to logger

    try:

        logger.info(LOGO)
        logger.info("Starting script")

        # Check env vars and connects
        if SA_SECRETS_FILE is None:
            logger.error("Env var SA_SECRETS_FILE missing")
            sys.exit(1)
        
        credentials = service_account.Credentials.from_service_account_file(SA_SECRETS_FILE, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)

        # Do tasks

        if args.ls:
            
            cd_folder, = args.ls
            
            page_token = None
            while True:

                if cd_folder == "ALL":
                    q = ""
                else:
                    q = "'{0}' in parents".format(cd_folder)

                # Try to list files, suppress errors
                try:
                    response = drive_service.files().list(pageSize=100, fields="nextPageToken, files(id, name)", pageToken=page_token, q=q).execute()
                    items = response.get('files', [])
                    page_token = response.get('nextPageToken', None)
                except Exception as e:
                    logger.error('Listing in folder ID {0} failed'.format(cd_folder))
                    logger.info("Caught exception on execution:")
                    logger.info(e)
                    sys.exit(1)

                # Empty out list, log only
                if not items:
                    logger.info('no files found')

                else:
                    for item in items:
                        print('{0} {1}'.format(item['id'], item['name']))
                        logger.info('{0} {1}'.format(item['id'], item['name']))

                if page_token is None:
                    break

            logger.info("Finished script")
            sys.exit(0)

        if args.rm:
           
            file_id, = args.rm

            try:

                drive_service.files().delete(fileId=file_id).execute()

            except Exception as e:
                logger.error('Deleting {0} failed'.format(file_id))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.mkdir:
            
            in_id, folder_name = args.mkdir

            try:

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
                    print('{0}'.format(folder['id']))
                    logger.info('{0}'.format(folder['id']))

                else:
                    
                    # Print already found file ID
                    print('{0}'.format(items[0]['id']))
                    logger.info('{0}'.format(items[0]['id']))

            except Exception as e:
                logger.error('Creating {0} in folder ID {1} failed'.format(folder_name, in_id))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.cp:
            
            source_id, cd_id, file_name = args.cp
            
            try:

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
                    print('{0}'.format(new_file['id']))
                    logger.info('{0}'.format(new_file['id']))

            except Exception as e:
                logger.error('Copying of {0} with name {1} in folder ID {2} failed'.format(source_id, file_name, cd_id))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)

            logger.info("Finished script")
            sys.exit(0)

        if args.pdf:
            
            file_id, file_name = args.pdf
            
            try:

                request = drive_service.files().export_media(fileId=file_id, mimeType='application/pdf')

                fh = io.FileIO(file_name, "wb")
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while done is False:
                    status, done = downloader.next_chunk()
                    print("Download {0}".format(status.progress() * 100))
                    logger.info("Download {0}".format(status.progress() * 100))
                fh.close()

            except Exception as e:
                logger.error('Downloading of {0} as {1} failed'.format(file_id, file_name))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)

            logger.info("Finished script")
            sys.exit(0)

        if args.upload:
            
            file_local, cd_id, file_name = args.upload
            
            try:

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
                    print('{0}'.format(new_file['id']))
                    logger.info('{0}'.format(new_file['id']))

            except Exception as e:
                logger.error('Uploading of {0} with name {1} in folder ID {2} failed'.format(file_local, file_name, cd_id))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)

            logger.info("Finished script")
            sys.exit(0)

    # Reroute catched exception to log
    except Exception as e:
        logger.exception(e)
        logger.info("Finished script with errors")
        sys.exit(1)

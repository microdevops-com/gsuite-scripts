#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *

# Import ext libs
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account

# Constants
LOGO="G Suite Scripts / Drive"
WORK_DIR = "/opt/sysadmws/gsuite-scripts"
LOG_DIR = "/opt/sysadmws/gsuite-scripts/log"
LOG_FILE = "drive.log"
SCOPES = ['https://www.googleapis.com/auth/drive']
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main
if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with G Suite Drive.')
    parser.add_argument("--debug", dest="debug", help="enable debug", action="store_true")
    parser.add_argument("--cd", dest="cd", help="operate in folder specified by ID")
    parser.add_argument("--ls", dest="ls", help="list files, optionaly with --cd", action="store_true")
    parser.add_argument("--mkdir", dest="mkdir", help="create folder, use with --cd")
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

        # Chdir to work dir
        os.chdir(WORK_DIR)

        # Check env vars and connects
        if args.ls or args.mkdir is not None:
            
            if SA_SECRETS_FILE is None:
                logger.error("Env var SA_SECRETS_FILE missing")
                sys.exit(1)
        
        if args.ls or args.mkdir is not None:
            
            credentials = service_account.Credentials.from_service_account_file(SA_SECRETS_FILE, scopes=SCOPES)
            drive_service = build('drive', 'v3', credentials=credentials)

        # Do tasks
        if args.ls:
            
            try:

                page_token = None
                while True:

                    if args.cd is not None:
                        q = "'{0}' in parents".format(args.cd)
                    else:
                        q = ""

                    response = drive_service.files().list(pageSize=100, fields="nextPageToken, files(id, name)", pageToken=page_token, q=q).execute()
                    items = response.get('files', [])

                    if not items:
                        print('No files found')
                        logger.info('No files found')

                    else:
                        for item in items:
                            print('{0} {1}'.format(item['id'], item['name']))
                            logger.info('ls: {0} {1}'.format(item['id'], item['name']))

                    page_token = response.get('nextPageToken', None)

                    if page_token is None:
                        break

            except Exception as e:
                logger.error("Caught exception on execution:")
                logger.exception(e)
                sys.exit(1)

        if args.mkdir:
            
            if args.cd is None:
                logger.error("--cd FOLDER_ID is required for --mkdir command")
                sys.exit(1)

            try:

                body = {
                    'name': args.mkdir,
                    'mimeType': "application/vnd.google-apps.folder",
                    'parents': [args.cd]
                }

                folder = drive_service.files().create(body = body).execute()
                print('Folder ID: {0}'.format(folder['id']))
                logger.info('Folder ID: {0}'.format(folder['id']))

            except Exception as e:
                logger.error("Caught exception on execution:")
                logger.exception(e)
                sys.exit(1)

    # Reroute catched exception to log
    except Exception as e:
        logger.exception(e)
        logger.info("Finished script with errors")
        sys.exit(1)

    logger.info("Finished script")

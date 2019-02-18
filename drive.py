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
    parser.add_argument("--dry-run", dest="dry_run", help="no new objects created or commits to db on reports", action="store_true")
    parser.add_argument("--list-sa-files", dest="list_sa_files", help="list all files available to service account", action="store_true")
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
        if args.list_sa_files:
            
            if SA_SECRETS_FILE is None:
                logger.error("Env var SA_SECRETS_FILE missing")
                sys.exit(1)
        
        if args.list_sa_files:
            
            credentials = service_account.Credentials.from_service_account_file(SA_SECRETS_FILE, scopes=SCOPES)
            drive_service = build('drive', 'v2', credentials=credentials)

        # Do tasks
        if args.list_sa_files:
            
            try:

                page_token = None
                while True:

                    response = drive_service.files().list(spaces='drive', fields='nextPageToken, items(id, title)', pageToken=page_token).execute()
                    for file in response.get('items', []):
                        logger.info('Found file: {0} {1}'.format(file.get('title'), file.get('id')))
                    page_token = response.get('nextPageToken', None)

                    if page_token is None:
                        break

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

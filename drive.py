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
    parser.add_argument("--cd", dest="cd", help="operate in folder specified by google drive ID CD")
    parser.add_argument("--name", dest="name", help="give new file name NAME, if required by command")
    parser.add_argument("--ls", dest="ls", help="returns ID<space>name of files, optionally with --cd", action="store_true")
    parser.add_argument("--mkdir", dest="mkdir", help="create folder named MKDIR, only if it does not exist yet, returns ID of created or found folder, use always with --cd")
    parser.add_argument("--cp", dest="cp", help="copy file referenced by google drive ID CP only if it does not exist yet, returns ID of created file if created, use always with --cd and --name")
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
        if SA_SECRETS_FILE is None:
            logger.error("Env var SA_SECRETS_FILE missing")
            sys.exit(1)
        
        credentials = service_account.Credentials.from_service_account_file(SA_SECRETS_FILE, scopes=SCOPES)
        drive_service = build('drive', 'v3', credentials=credentials)

        # Do tasks
        if args.ls:
            
            page_token = None
            while True:

                if args.cd is not None:
                    q = "'{0}' in parents".format(args.cd)
                else:
                    q = ""

                # Try to list files, suppress errors
                try:
                    response = drive_service.files().list(pageSize=100, fields="nextPageToken, files(id, name)", pageToken=page_token, q=q).execute()
                    items = response.get('files', [])
                    page_token = response.get('nextPageToken', None)
                except Exception as e:
                    logger.error('Listing in folder ID {0} failed'.format(args.cd))
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

        if args.mkdir:
            
            if args.cd is None:
                logger.error("--cd ID is required for --mkdir command")
                sys.exit(1)

            try:

                # Query if the same file already exists
                q = "'{0}' in parents and name = '{1}'".format(args.cd, args.mkdir)

                # Get only one page with 1 result
                response = drive_service.files().list(pageSize=1, fields="files(id, name)", q=q).execute()
                items = response.get('files', [])

                if not items:

                    body = {
                        'name': args.mkdir,
                        'mimeType': "application/vnd.google-apps.folder",
                        'parents': [args.cd]
                    }

                    folder = drive_service.files().create(body = body).execute()
                    print('{0}'.format(folder['id']))
                    logger.info('{0}'.format(folder['id']))

                else:
                    
                    # Print already found file ID
                    print('{0}'.format(items[0]['id']))
                    logger.info('{0}'.format(items[0]['id']))

            except Exception as e:
                logger.error('Creating {0} in folder ID {1} failed'.format(args.mkdir, args.cd))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)

        if args.cp:
            
            if args.cd is None:
                logger.error("--cd ID is required for --cp command")
                sys.exit(1)
            
            if args.name is None:
                logger.error("--name NAME is required for --cp command")
                sys.exit(1)

            try:

                # Query if the same file already exists
                q = "'{0}' in parents and name = '{1}'".format(args.cd, args.name)

                # Get only one page with 1 result
                response = drive_service.files().list(pageSize=1, fields="files(id, name)", q=q).execute()
                items = response.get('files', [])

                if not items:

                    body = {
                        'name': args.name,
                        'parents': [args.cd]
                    }

                    new_file = drive_service.files().copy(fileId=args.cp, body = body).execute()
                    print('{0}'.format(new_file['id']))
                    logger.info('{0}'.format(new_file['id']))

            except Exception as e:
                logger.error('Copying of {0} with name {1} in folder ID {2} failed'.format(args.cp, args.name, args.cd))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)

    # Reroute catched exception to log
    except Exception as e:
        logger.exception(e)
        logger.info("Finished script with errors")
        sys.exit(1)

    logger.info("Finished script")

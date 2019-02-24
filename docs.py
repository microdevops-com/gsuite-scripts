#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *

# Import ext libs
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account

# Constants
LOGO="G Suite Scripts / Docs"
WORK_DIR = "/opt/sysadmws/gsuite-scripts"
LOG_DIR = "/opt/sysadmws/gsuite-scripts/log"
LOG_FILE = "docs.log"
SCOPES = ['https://www.googleapis.com/auth/documents']
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main
if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with G Suite Docs.')
    parser.add_argument("--debug", dest="debug", help="enable debug", action="store_true")
    parser.add_argument("--replace-all-text", dest="replace_all_text", help="substitute templates (for example {{ client }} or __DATE__) within google drive doc referenced by ID REPLACE_ALL_TEXT")
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
        docs_service = build('docs', 'v1', credentials=credentials)

        # Do tasks
        if args.replace_all_text:
            
            try:

                client_name = 'Roga i Kopyta'
                date = datetime.datetime.now().strftime("%y/%m/%d")

                requests = [
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': '__CLIENT_NAME__',
                                'matchCase':  'true'
                            },
                            'replaceText': client_name,
                        }
                    },
                    {
                        'replaceAllText': {
                            'containsText': {
                                'text': '__DATE__',
                                'matchCase':  'true'
                            },
                            'replaceText': str(date),
                        }
                    }
                ]

                response = docs_service.documents().batchUpdate(documentId=args.replace_all_text, body={'requests': requests}).execute()
                print("Execution response: %s" % str(response))

            except Exception as e:
                logger.error('Document {0} replacing all text failed'.format(args.replace_all_text))
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

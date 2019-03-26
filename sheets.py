#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *

# Import ext libs
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account

# Constants
LOGO="G Suite Scripts / Sheets"
WORK_DIR = "/opt/sysadmws/gsuite-scripts"
LOG_DIR = "/opt/sysadmws/gsuite-scripts/log"
LOG_FILE = "sheets.log"
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main

if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with G Suite Docs.')
    parser.add_argument("--debug",              dest="debug",               help="enable debug",                        action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    get_as_json_help = """get google drive spreadsheet ID range RANGE on sheet SHEET as json, use
                          DIMENSION = 'ROWS' or 'COLUMNS',
                          RENDER = 'FORMATTED_VALUE' or 'UNFORMATTED_VALUE' or 'FORMULA',
                          DATETIME_RENDER = 'SERIAL_NUMBER' or 'FORMATTED_STRING'"""
    group.add_argument("--get-as-json",         dest="get_as_json",         help=get_as_json_help,                      nargs=6,    metavar=("ID", "SHEET", "RANGE", "DIMENSION", "RENDER", "DATETIME_RENDER"))
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
        sheets_service = build('sheets', 'v4', credentials=credentials)

        # Do tasks

        if args.get_as_json:
            
            try:

                spreadsheet_id, sheet_id, range_id, dimension, render, datetime_render = args.get_as_json

                sheet = sheets_service.spreadsheets()
                result = sheet.values().get(spreadsheetId=spreadsheet_id, range="{0}!{1}".format(sheet_id, range_id), majorDimension=dimension, valueRenderOption=render, dateTimeRenderOption=datetime_render).execute()
                values = result.get('values', [])

                print(json.dumps(values, indent=4))
                logger.info(json.dumps(values))

            except Exception as e:
                logger.error('Getting spreadsheet {0} sheet {1} range {2} failed'.format(spreadsheet_id, sheet_id, range_id))
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

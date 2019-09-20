#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *
from gsuite_scripts import *

# Constants
LOGO="G Suite Scripts / Sheets"
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "log"
LOG_FILE = "sheets.log"
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
    append_data_help = """append table defined by RANGE (e.g. A:B) within google drive spreadsheet ID on sheet SHEET,
                         data (one or multiple rows or columns) is provided with JSON (e.g. [["Cell 1 1", "Cell 1 2"], ["Cell 2 1", "Cell 2 2"]]),
                         use DIMENSION = 'ROWS' or 'COLUMNS'"""
    group.add_argument("--append-data",         dest="append_data",         help=append_data_help,                       nargs=5,    metavar=("ID", "SHEET", "RANGE", "DIMENSION", "JSON"))
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
            raise Exception("Env var SA_SECRETS_FILE missing")
        
        # Do tasks

        if args.get_as_json:
            
            try:

                spreadsheet_id, sheet_id, range_id, dimension, render, datetime_render = args.get_as_json

                response = sheets_get_as_json(SA_SECRETS_FILE, spreadsheet_id, sheet_id, range_id, dimension, render, datetime_render)

                print(json.dumps(response, indent=4))
                logger.info(json.dumps(response))

            except Exception as e:
                raise Exception('Getting spreadsheet {0} sheet {1} range {2} failed'.format(spreadsheet_id, sheet_id, range_id))
            
        if args.append_data:
            
            try:

                spreadsheet_id, sheet_id, range_id, dimension, json_str = args.append_data

                response = sheets_append_data(SA_SECRETS_FILE, spreadsheet_id, sheet_id, range_id, dimension, json_str)
                print(response)
                logger.info(response)


            except Exception as e:
                raise Exception('Getting spreadsheet {0} sheet {1} range {2} failed'.format(spreadsheet_id, sheet_id, range_id))
            
    # Reroute catched exception to log
    except Exception as e:
        logger.exception(e)
        logger.info("Finished script with errors")
        sys.exit(1)
            
    logger.info("Finished script")

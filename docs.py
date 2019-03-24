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
    parser.add_argument("--get", dest="get", help="get as JSON google drive doc referenced by ID GET")
    parser.add_argument("--get-table-index", dest="get_table_index", help="get startIndex of table within google drive doc referenced by ID GET_TABLE_INDEX, always use with --table")
    parser.add_argument("--table", dest="table", help="table number TABLE to search within google drive doc, starting with 1")
    parser.add_argument("--replace-all-text", dest="replace_all_text", help="replace all text templates within google drive doc referenced by ID REPLACE_ALL_TEXT, always use with --templates")
    parser.add_argument("--templates", dest="templates", help="JSON of templates, e.g. --templates '{\"__KEY1__\": \"Value 1\", \"__KEY2__\": \"Value 2\"}'", type=json.loads)
    parser.add_argument("--insert-table-row", dest="insert_table_row", help="insert row into table within google drive doc referenced by ID INSERT_TABLE_ROW, always use with --table-index TABLE and --row")
    parser.add_argument("--table-index", dest="table_index", help="table with startIndex TABLE_INDEX within google drive doc to which insert the row")
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
        if args.get:

            try:

                response = docs_service.documents().get(documentId=args.get).execute()
                print("{0}".format(json.dumps(response, indent=4)))
                logger.info("{0}".format(json.dumps(response)))

            except Exception as e:
                logger.error('Getting document {0} failled'.format(args.get))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.get_table_index:

            if args.table is None:
                logger.error("--table TABLE is required for --get-table-index")
                sys.exit(1)
            
            try:

                response = docs_service.documents().get(documentId=args.get_table_index).execute()
                
                content = response['body']['content']
                table_index = 0

                for element in content:

                    if "table" in element:

                        table_index += 1
                        if int(table_index) == int(args.table):

                            print("{0}".format(element['startIndex']))
                            logger.info("{0}".format(element['startIndex']))

            except Exception as e:
                logger.error('Getting table {0} index from document {1} failed'.format(args.table, args.get_table_index))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.replace_all_text:

            if args.templates is None:
                logger.error("--templates JSON is required for --replace-all-text")
                sys.exit(1)
            
            try:

                requests = []

                for template in args.templates:

                    requests = requests + [
                        {
                            'replaceAllText': {
                                'containsText': {
                                    'text': template,
                                    'matchCase':  'true'
                                },
                                'replaceText': args.templates[template]
                            }
                        }
                    ]

                response = docs_service.documents().batchUpdate(documentId=args.replace_all_text, body={'requests': requests}).execute()
                print("{0}".format(response))
                logger.info("{0}".format(response))

            except Exception as e:
                logger.error('Document {0} replacing all text templates failed'.format(args.replace_all_text))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.insert_table_row:
            
            if args.table_index is None:
                logger.error("--table-index TABLE_INDEX is required for --insert-table-row")
                sys.exit(1)

            try:

                requests = [
                    {
                        'insertTableRow': {
                            'tableCellLocation': {
                                'tableStartLocation': {
                                    'index': args.table_index
                                },
                                'rowIndex': 1,
                                'columnIndex': 0
                            },
                            'insertBelow': 'true'
                        }
                    }
                ]

                response = docs_service.documents().batchUpdate(documentId=args.insert_table_row, body={'requests': requests}).execute()
                print("{0}".format(response))
                logger.info("{0}".format(response))

            except Exception as e:
                logger.error('Document {0} inserting row into table failed'.format(args.insert_table_row))
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

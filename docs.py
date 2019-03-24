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
    parser.add_argument("--debug",              dest="debug",               help="enable debug",                                                                    action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--get-as-json",         dest="get_as_json",         help="get google drive doc ID as json",                                                 nargs=1,    metavar=("ID"))
    group.add_argument("--get-table-index",     dest="get_table_index",     help="get startIndex of table N within google drive doc ID, N starts from 1",           nargs=2,    metavar=("ID", "N"))
    group.add_argument("--replace-all-text",    dest="replace_all_text",
        help="replace all text templates defined by JSON (e.g. '{\"__KEY1__\": \"Value 1\", \"__KEY2__\": \"Value 2\"}') within google drive doc ID",               nargs=2,    metavar=("ID", "JSON"))
    group.add_argument("--insert-table-row",    dest="insert_table_row",
        help="insert row defined by JSON (e.g. '{\"Cell 1\", \"Cell 2\"}') into table with startIndex TABLE_INDEX (use --get-table-index to get startIndex) below row number BELOW_ROW_NUMBER within google drive doc ID",
                                                                                                                                                                    nargs=4,    metavar=("ID", "TABLE_INDEX", "BELOW_ROW_NUMBER", "JSON"))
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
        if args.get_as_json:

            try:

                doc_id, = args.get_as_json

                response = docs_service.documents().get(documentId=doc_id).execute()
                print("{0}".format(json.dumps(response, indent=4)))
                logger.info("{0}".format(json.dumps(response)))

            except Exception as e:
                logger.error('Getting document {0} failled'.format(doc_id))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.get_table_index:

            try:

                doc_id, table_n = args.get_table_index
                
                response = docs_service.documents().get(documentId=doc_id).execute()
                
                content = response['body']['content']
                table_index = 0

                for element in content:

                    if "table" in element:

                        table_index += 1
                        if int(table_index) == int(table_n):

                            print("{0}".format(element['startIndex']))
                            logger.info("{0}".format(element['startIndex']))

            except Exception as e:
                logger.error('Getting table {0} index from document {1} failed'.format(table_n, doc_id))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.replace_all_text:

            try:

                doc_id, json_str = args.replace_all_text
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
                print("{0}".format(response))
                logger.info("{0}".format(response))

            except Exception as e:
                logger.error('Document {0} replacing all text templates {1} failed'.format(doc_id, json_str))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.insert_table_row:
            
            try:

                doc_id, table_index, below_row_number, json_str = args.insert_table_row
                json_dict = json.loads(json_str)
                row_index = int(below_row_number) - 1
                table_index = int(table_index)
                
                requests = [
                    {
                        'insertTableRow': {
                            'tableCellLocation': {
                                'tableStartLocation': {
                                    'index': table_index
                                },
                                'rowIndex': row_index,
                                'columnIndex': 0
                            },
                            'insertBelow': 'true'
                        }
                    }
                ]

                response = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
                print("{0}".format(response))
                logger.info("{0}".format(response))

            except Exception as e:
                logger.error('Document {0} inserting row json {1} below {2} into table {3} failed'.format(doc_id, json_str, below_row_number, table_index))
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

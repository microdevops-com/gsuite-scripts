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
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "/opt/sysadmws/gsuite-scripts/log"
LOG_FILE = "docs.log"
SCOPES = ['https://www.googleapis.com/auth/documents']
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main

if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with G Suite Docs.')
    parser.add_argument("--debug",              dest="debug",               help="enable debug",                        action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--get-as-json",         dest="get_as_json",         help="get google drive doc ID as json",     nargs=1,    metavar=("ID"))
    replace_all_text_help = "replace all text templates defined by JSON (e.g. '{\"__KEY1__\": \"Value 1\", \"__KEY2__\": \"Value 2\"}') within google drive doc ID"
    group.add_argument("--replace-all-text",    dest="replace_all_text",    help=replace_all_text_help,                 nargs=2,    metavar=("ID", "JSON"))
    insert_table_row_help = "insert row defined by JSON (e.g. '[\"Cell 1\", \"Cell 2\"]') into TABLE_NUM (table count starts from 1) below row number BELOW_ROW_NUMBER within google drive doc ID"
    group.add_argument("--insert-table-row",    dest="insert_table_row",    help=insert_table_row_help,                 nargs=4,    metavar=("ID", "TABLE_NUM", "BELOW_ROW_NUMBER", "JSON"))
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
        docs_service = build('docs', 'v1', credentials=credentials)

        # Do tasks

        if args.get_as_json:

            try:

                doc_id, = args.get_as_json

                response = docs_service.documents().get(documentId=doc_id).execute()
                print(json.dumps(response, indent=4))
                logger.info(json.dumps(response))

            except Exception as e:
                logger.error('Getting document {0} failled'.format(doc_id))
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
                print(response)
                logger.info(response)

            except Exception as e:
                logger.error('Document {0} replacing all text templates {1} failed'.format(doc_id, json_str))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.insert_table_row:
            
            try:

                doc_id, table_num, below_row_number, json_str = args.insert_table_row
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
                            logger.info("Table index: {0}".format(table_index))

                            # Save endIndex of the row below which we will insert
                            # We can calc new row first cell startIndex by this endIndex
                            
                            table = element['table']
                            rows = table['tableRows']
                            row_n = 0
                            row_end_index = None

                            # Check if requested below_row_num is out of table rows
                            if int(below_row_number) > len(rows):
                                logger.error("Table {0} has less than {1} rows ({2} actually), exiting".format(table_num, below_row_number, len(rows)))
                                sys.exit(1)
                            
                            for row in rows: # For some reason row[x] doesn't work, so just iterate
                                
                                row_n += 1
                                if row_n == int(below_row_number):

                                    row_end_index = int(row['endIndex'])
                                    logger.info("Row endIndex: {0}".format(row_end_index))

                            if row_end_index is None:
                                logger.error("Row {0} index for table {1} not found, exiting".format(below_row_number, table_num))

                if table_index is None:
                    logger.error("Table index for TABLE_NUM = {0} not found, exiting".format(table_num))
                    sys.exit(1)
                
                # Insert new row

                requests = [
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

                response = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
                print(response)
                logger.info(response)

                # Fill row values
                # As per https://developers.google.com/docs/api/how-tos/best-practices data should be filled backwards
                
                requests = []
                list_n = 0

                json_list.reverse()
                for json_item in json_list:

                    requests = requests + [
                        {
                            'insertText': {
                                'location': {
                                    'index': row_end_index + ( 2 * (len(json_list) - list_n) )
                                },
                                'text': json_item
                            }
                        }
                    ]

                    list_n += 1

                response = docs_service.documents().batchUpdate(documentId=doc_id, body={'requests': requests}).execute()
                print(response)
                logger.info(response)

            except Exception as e:
                logger.error('Document {0} inserting row json {1} below {2} into table {3} failed'.format(doc_id, json_str, below_row_number, table_num))
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

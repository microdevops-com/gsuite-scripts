#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *
from gsuite_scripts import *

# Constants
LOGO="G Suite Scripts / Docs"
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "log"
LOG_FILE = "docs.log"
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
    insert_table_rows_help = "insert rows defined by JSON (e.g. '[[\"Cell 1-1\", \"Cell 1-2\"], [\"Cell 2-1\", \"Cell 2-2\"]]') into TABLE_NUM (table, row count starts from 1) below row number BELOW_ROW_NUMBER within google drive doc ID"
    group.add_argument("--insert-table-rows",   dest="insert_table_rows",   help=insert_table_rows_help,                nargs=4,    metavar=("ID", "TABLE_NUM", "BELOW_ROW_NUMBER", "JSON"))
    delete_table_row_help = "delete row ROW_NUMBER from TABLE_NUM (table, row count starts from 1) within google drive doc ID"
    group.add_argument("--delete-table-row",    dest="delete_table_row",    help=delete_table_row_help,                 nargs=3,    metavar=("ID", "TABLE_NUM", "ROW_NUMBER"))
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
        
        # Do tasks

        if args.get_as_json:
        
            try:

                doc_id, = args.get_as_json

                response = docs_get_as_json(SA_SECRETS_FILE, doc_id)

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
                
                response = docs_replace_all_text(SA_SECRETS_FILE, doc_id, json_str)

                print(response)
                logger.info(response)

            except Exception as e:
                logger.error('Document {0} replacing all text templates {1} failed'.format(doc_id, json_str))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)

        if args.insert_table_rows:
            
            try:

                doc_id, table_num, below_row_number, json_str = args.insert_table_rows
                
                response = docs_insert_table_rows(SA_SECRETS_FILE, doc_id, table_num, below_row_number, json_str)

                print(response)
                logger.info(response)

            except Exception as e:
                logger.error('Document {0} inserting row json {1} below {2} into table {3} failed'.format(doc_id, json_str, below_row_number, table_num))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)

        if args.delete_table_row:
            
            try:

                doc_id, table_num, row_number = args.delete_table_row
                
                response_delete_row = docs_delete_table_row(SA_SECRETS_FILE, doc_id, table_num, row_number)

                print(response_delete_row)
                logger.info(response_delete_row)

            except Exception as e:
                logger.error('Document {0} deleting row {1} from table {2} failed'.format(doc_id, row_number, table_num))
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

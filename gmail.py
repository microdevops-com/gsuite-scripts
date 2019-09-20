#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *
from gsuite_scripts import *

# Constants
LOGO="G Suite Scripts / Gmail"
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "log"
LOG_FILE = "gmail.log"
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main

if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with Gmail.')
    parser.add_argument("--debug",              dest="debug",               help="enable debug",                        action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    create_draft_help = """create draft inside USER gmail, from email FROM to email(s) TO, CC, BCC with SUBJECT and TEXT, and attach local files listed with json list ATTACH,
                           e.g. --create-draft me@example.com '"Me Myself" <me@example.com>' '"Client 1" <client1@acme.com>, "Client 2" <client2@acme.com>' '"Someone Other" cc@acme.com' 'bcc@acme.com' 'Subject may contain UTF - перевірка チェックする' 'Message may contain UTF and new\\nlines\\nперевірка\\nチェックする' '["a.pdf", "b.pdf"]'"""
    group.add_argument("--create-draft",        dest="create_draft",        help=create_draft_help,                     nargs=8,    metavar=("USER", "FROM", "TO", "CC", "BCC", "SUBJECT", "TEXT", "ATTACH"))
    send_draft_help = "send draft DRAFT_ID inside USER gmail"
    group.add_argument("--send-draft",          dest="send_draft",          help=send_draft_help,                       nargs=2,    metavar=("USER", "DRAFT_ID"))
    list_messages_help = "list messages available to gmail USER"
    group.add_argument("--list-messages",       dest="list_messages",       help=list_messages_help,                    nargs=1,    metavar=("USER"))
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

        if args.create_draft:
            
            try:
            
                gmail_user, message_from, message_to, message_cc, message_bcc, message_subject, message_text, attach_str = args.create_draft

                draft_id, draft_message = gmail_create_draft(SA_SECRETS_FILE, gmail_user, message_from, message_to, message_cc, message_bcc, message_subject, message_text, attach_str)

                print("Draft {0} with message {1} created".format(draft_id, draft_message))
                logger.info("Draft {0} with message {1} created".format(draft_id, draft_message))

            except Exception as e:
                raise Exception('Creating draft for user {0} failed'.format(gmail_user))
            
        if args.list_messages:
            
            try:
            
                gmail_user, = args.list_messages

                response = gmail_list_messages(SA_SECRETS_FILE, gmail_user)

                for item in response:
                    print(item)
                    logger.info(item)

            except Exception as e:
                raise Exception('Listing messages for user {0} failed'.format(gmail_user))
            
        if args.send_draft:
            
            try:
            
                gmail_user, draft_id = args.send_draft

                message = gmail_send_draft(SA_SECRETS_FILE, gmail_user, draft_id)

                print("Message {0} sent, labels: {1}".format(message["id"], message["labelIds"]))
                logger.info("Message {0} sent, labels: {1}".format(message["id"], message["labelIds"]))

            except Exception as e:
                raise Exception('Sending draft for user {0} failed'.format(gmail_user))
            
    # Reroute catched exception to log
    except Exception as e:
        logger.exception(e)
        logger.info("Finished script with errors")
        sys.exit(1)
            
    logger.info("Finished script")

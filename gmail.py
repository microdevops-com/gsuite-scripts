#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *

# Import ext libs
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account
import base64
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
import mimetypes
from email import encoders

# Constants
LOGO="G Suite Scripts / Gmail"
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "/opt/sysadmws/gsuite-scripts/log"
LOG_FILE = "gmail.log"
SCOPES = [
        'https://mail.google.com/',
        'https://www.googleapis.com/auth/gmail.compose',
        #'https://www.googleapis.com/auth/gmail.metadata', with this scope you cannot get messages
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.send'
]
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
            logger.error("Env var SA_SECRETS_FILE missing")
            sys.exit(1)
        
        # Do tasks

        if args.create_draft:
            
            gmail_user, message_from, message_to, message_cc, message_bcc, message_subject, message_text, attach_str = args.create_draft
            message_text_new_lines = message_text.replace('\\n', '\n')
            attach_dict = json.loads(attach_str)

            try:

                credentials = service_account.Credentials.from_service_account_file(SA_SECRETS_FILE, scopes=SCOPES)
                delegated_credentials = credentials.with_subject(gmail_user)
                gmail_service = build('gmail', 'v1', credentials=delegated_credentials)
            
                message = MIMEMultipart()
                message['From'] = message_from
                message['To'] = message_to
                message['Cc'] = message_cc
                message['Bcc'] = message_bcc
                message['Subject'] = message_subject
                
                message.attach(MIMEText(message_text_new_lines, "plain"))

                for file_name in attach_dict:

                    with open(file_name, "rb") as attachment:

                        part = MIMEBase("application", "octet-stream")
                        part.set_payload(attachment.read())

                    encoders.encode_base64(part)
                    part.add_header("Content-Disposition", "attachment", filename=os.path.basename(file_name))
                    message.attach(part)
                
                b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
                b64_string = b64_bytes.decode()
                message_body = {'raw': b64_string}
                message = {'message': message_body}
                draft = gmail_service.users().drafts().create(userId='me', body=message).execute()

                print("Draft {0} with message {1} created".format(draft['id'], draft['message']))
                logger.info("Draft {0} with message {1} created".format(draft['id'], draft['message']))

            except Exception as e:
                logger.error('Creating draft for user {0} failed'.format(gmail_user))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)
        
        if args.list_messages:
            
            gmail_user, = args.list_messages

            try:

                credentials = service_account.Credentials.from_service_account_file(SA_SECRETS_FILE, scopes=SCOPES)
                delegated_credentials = credentials.with_subject(gmail_user)
                gmail_service = build('gmail', 'v1', credentials=delegated_credentials)

                response = gmail_service.users().messages().list(userId=gmail_user).execute()

                if 'messages' in response:
                    
                    for msg in response['messages']:
                        
                        message = gmail_service.users().messages().get(userId=gmail_user, id=msg['id'], format='raw').execute()
                        print(msg)
                        print(message['snippet'])
                        logger.info(msg)
                        logger.info(message['snippet'])

            except Exception as e:
                logger.error('Listing messages for user {0} failed'.format(gmail_user))
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

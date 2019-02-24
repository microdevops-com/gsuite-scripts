#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *

# Import ext libs
from googleapiclient.discovery import build
import oauth2client.client
from google.oauth2 import service_account
import base64
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes

# Constants
LOGO="G Suite Scripts / Gmail"
WORK_DIR = "/opt/sysadmws/gsuite-scripts"
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
    parser.add_argument("--debug", dest="debug", help="enable debug", action="store_true")
    parser.add_argument("--create-draft", dest="create_draft", help="create draft email .................................")
    parser.add_argument("--list-messages", dest="list_messages", help="................................")
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
        delegated_credentials = credentials.with_subject('CHANGE_ME@example.com')
        gmail_service = build('gmail', 'v1', credentials=delegated_credentials)

        # Do tasks
        if args.create_draft:
            
            try:

                message = MIMEText("TEST .........")
                message['to'] = "CHANGE_ME@example.com"
                message['from'] = "CHANGE_ME@example.com"
                message['subject'] = "Test message"
                b64_bytes = base64.urlsafe_b64encode(message.as_bytes())
                b64_string = b64_bytes.decode()
                message_body = {'raw': b64_string}
                message = {'message': message_body}
                draft = gmail_service.users().drafts().create(userId='CHANGE_ME@example.com', body=message).execute()

                print('Draft id: %s\nDraft message: %s' % (draft['id'], draft['message']))

            except Exception as e:
                logger.error('......... {0} ............ failed'.format(args.create_draft))
                logger.info("Caught exception on execution:")
                logger.info(e)
                sys.exit(1)
            
            logger.info("Finished script")
            sys.exit(0)
        
        if args.list_messages:
            
            try:

                response = gmail_service.users().messages().list(userId='CHANGE_ME@example.com').execute()
                if 'messages' in response:
                    print(response['messages'])
                    for msg in response['messages']:
                        message = gmail_service.users().messages().get(userId='CHANGE_ME@example.com', id=msg['id'], format='raw').execute()
                        print('Message snippet: %s' % message['snippet'])



            except Exception as e:
                logger.error('......... {0} ............ failed'.format(args.list_messages))
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

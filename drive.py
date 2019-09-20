#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Import common code
from sysadmws_common import *
from gsuite_scripts import *

# Constants
LOGO="G Suite Scripts / Drive"
LOG_DIR = os.environ.get("LOG_DIR")
if LOG_DIR is None:
    LOG_DIR = "log"
LOG_FILE = "drive.log"
SA_SECRETS_FILE = os.environ.get("SA_SECRETS_FILE")

# Main

if __name__ == "__main__":

    # Set parser and parse args
    parser = argparse.ArgumentParser(description='Script to automate specific operations with G Suite Drive.')
    parser.add_argument("--debug",              dest="debug",               help="enable debug",                        action="store_true")
    group = parser.add_mutually_exclusive_group(required=True)
    ls_help = "returns id<space>name<mimeType> of files available in folder ID, use ID = ALL to list all available files"
    group.add_argument("--ls",                  dest="ls",                  help=ls_help,                               nargs=1,    metavar=("ID"))
    rm_help = "delete file ID (folders are also files in drive)"
    group.add_argument("--rm",                  dest="rm",                  help=rm_help,                               nargs=1,    metavar=("ID"))
    mkdir_help = "create folder NAME within folder ID, only if NAME does not exist yet, returns ID of created or found folder"
    group.add_argument("--mkdir",               dest="mkdir",               help=mkdir_help,                            nargs=2,    metavar=("ID", "NAME"))
    cp_help = "copy source file ID to folder CD with NAME, only if it does not exist yet, returns ID of created file if created"
    group.add_argument("--cp",                  dest="cp",                  help=cp_help,                               nargs=3,    metavar=("ID", "CD", "NAME"))
    group.add_argument("--pdf",                 dest="pdf",                 help="download file ID as pdf file NAME",   nargs=2,    metavar=("ID", "NAME"))
    group.add_argument("--download",            dest="download",            help="download file ID as file NAME",       nargs=2,    metavar=("ID", "NAME"))
    upload_help = "upload local FILE as NAME to google drive folder CD, only if it does not exist yet, returns ID of created file if created"
    group.add_argument("--upload",              dest="upload",              help=upload_help,                           nargs=3,    metavar=("FILE", "CD", "NAME"))
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

        if args.ls:
            
            try:

                cd_folder, = args.ls

                items = drive_ls(SA_SECRETS_FILE, cd_folder)
            
                if not items:
                    logger.info('no files found')
                else:
                    for item in items:
                        print('{0} {1} {2}'.format(item['id'], item['name'], item['mimeType']))
                        logger.info('{0} {1} {2}'.format(item['id'], item['name'], item['mimeType']))

            except Exception as e:
                raise Exception('Listing {0} failed'.format(cd_folder))

        if args.rm:
           
            try:
            
                file_id, = args.rm

                response = drive_rm(SA_SECRETS_FILE, file_id)
                print(response)
                logger.info(response)

            except Exception as e:
                raise Exception('Deleting {0} failed'.format(file_id))
            
        if args.mkdir:
            
            try:
            
                in_id, folder_name = args.mkdir

                response = drive_mkdir(SA_SECRETS_FILE, in_id, folder_name)
                print(response)
                logger.info(response)

            except Exception as e:
                raise Exception('Creating {0} in folder ID {1} failed'.format(folder_name, in_id))
            
        if args.cp:
            
            try:
            
                source_id, cd_id, file_name = args.cp

                response = drive_cp(SA_SECRETS_FILE, source_id, cd_id, file_name)
                print(response)
                logger.info(response)

            except Exception as e:
                raise Exception('Copying of {0} with name {1} in folder ID {2} failed'.format(source_id, file_name, cd_id))

        if args.pdf:
            
            try:
            
                file_id, file_name = args.pdf
                
                response = drive_pdf(SA_SECRETS_FILE, file_id, file_name)
                print(response)
                logger.info(response)

            except Exception as e:
                raise Exception('Downloading of {0} as {1} failed'.format(file_id, file_name))

        if args.download:
            
            try:
            
                file_id, file_name = args.download
                
                response = drive_download(SA_SECRETS_FILE, file_id, file_name)
                print(response)
                logger.info(response)

            except Exception as e:
                raise Exception('Downloading of {0} as {1} failed'.format(file_id, file_name))

        if args.upload:
            
            try:
            
                file_local, cd_id, file_name = args.upload

                response = drive_upload(SA_SECRETS_FILE, file_local, cd_id, file_name)
                print(response)
                logger.info(response)

            except Exception as e:
                raise Exception('Uploading of {0} with name {1} in folder ID {2} failed'.format(file_local, file_name, cd_id))

    # Reroute catched exception to log
    except Exception as e:
        logger.exception(e)
        logger.info("Finished script with errors")
        sys.exit(1)
            
    logger.info("Finished script")

from email.message import EmailMessage
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import re
from googleapiclient.discovery import build
import base64
from googleapiclient.errors import HttpError
from gmail_api.cs_gmail_cred.cred import *
from gmail_api.reply_and_label_email import *



def draft_and_label_email(service, id, send_body, debug_log, label_names, mode, send_subject = None):
    """Send an email message."""
    try:
        original_message = get_info_from_id(service, id)

        # alter the data when entering debug mode
        if mode == "debug":
            original_message, label_names, send_subject = debug_alteration(original_message, label_names)

        draft_message = create_message(original_message, send_subject, send_body, debug_log)
        drafted_message = service.users().drafts().create(userId="me", body=draft_message).execute()
        # print('draft Id: %s' % drafted_message['id'])

        # check if the label_names is empty, if yes, then dont run applied label
        if label_names:
            applied_label = apply_labels(service, label_names, original_message['thread_id'])
            print('Applied label: %s' % applied_label['labelIds'][0])
        
        remove_label_from_thread(service, 'Label_1274735915684369724', original_message['thread_id'])

        return drafted_message

        
    except HttpError as error:
        print(f'An error occurred: {error}')

        
# service = build('gmail', 'v1', credentials=authenticate())
# id = '18b08b895156de40'
# send_subject = ""
# send_body = "i am not able to do this 2"
# debug_log = ''
# label_names = ['resolved']

# # 2 different modes "debug" and "production"
# mode = "production"

# draft_and_label_email(service, id, send_subject, send_body, debug_log, label_names, mode)



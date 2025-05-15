from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from gmail_api.cs_gmail_cred.cred import authenticate

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import base64


def extract_body_from_message(message):
    """Extract the email body from the given message."""
    
    def decode_content(data_str):
        """Decode the content and return it."""
        try:
            return base64.urlsafe_b64decode(data_str).decode('utf-8', 'ignore')
        except (base64.binascii.Error, UnicodeDecodeError) as e:
            print(f"Error decoding data: {data_str}. Error: {e}")
            return ""

    def recursive_extraction(part):
        """Recursively extract the body content."""
        mimeType = part.get('mimeType')
        if mimeType in ['text/plain', 'text/html']:
            data_str = part.get('body', {}).get('data')
            if isinstance(data_str, str):
                return decode_content(data_str)
        elif 'parts' in part:
            plain_parts = [sp for sp in part['parts'] if sp.get('mimeType') == 'text/plain']
            if plain_parts:
                return recursive_extraction(plain_parts[0])
            for subpart in part['parts']:
                body_content = recursive_extraction(subpart)
                if body_content:
                    return body_content

        return ""

    # Start extracting from the top-level message
    return recursive_extraction(message['payload'])

def get_info_from_id(service, id):
    message = service.users().messages().get(userId='me', id=id).execute()
    payload = message['payload']
    headers = payload.get('headers')
    for item in headers:
        item['name'] = item['name'].lower()
    
    message_id = None
    subject = None
    from_email = None
    to_email = None
    date = None
    in_reply_to = None
    references = None
    thread_id = message['threadId']
    original_message_date = None
    original_message_time = None
    return_path = None

    for header in headers:
        name = header.get('name')
        value = header.get('value')
        if name == 'message-id':
            message_id = value
            in_reply_to = value
            references = value
        if name == 'subject':
            subject = value
        if name == 'from':
            from_email = value
        if name == 'to':
            to_email = value
        if name == 'date':
            date = value
        if name == 'return-path':
            return_path = value


    # get date and time
    try:
        parsed_datetime = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')
    except ValueError:
        # Assuming the timezone abbreviation is always 4 characters (including parentheses)
        # and there's always a space before it, like " (PDT)"
        date = date[:-6]
        parsed_datetime = datetime.strptime(date, '%a, %d %b %Y %H:%M:%S %z')

    original_message_date = parsed_datetime.strftime('%d %b %Y')
    original_message_time = parsed_datetime.strftime('%H:%M:%S')



    decoded_body = extract_body_from_message(message)

    original_message = {
        'message_id': message_id,
        'thread_id': thread_id,
        'subject': subject,
        'from_email': from_email,
        'to_email': to_email,
        'return_path': return_path,
        'date': date,
        'original_message_from': from_email,
        'original_message_date': original_message_date,
        'original_message_time': original_message_time,
        'in_reply_to': in_reply_to,
        'references': references,
        'body': decoded_body
        }

    return original_message

def json_to_html(data):
    html_string = "<html><head><style>table, th, td {border: 1px solid black;border-collapse: collapse;padding: 8px;}th {background-color: #f2f2f2;}</style></head><body>"

    # Loop through the main structure
    for loop, content in data.items():
        html_string += f"<h3>{loop}</h3>"
        html_string += "<table>"

        for entry in content:
            html_string += "<tr><th>Role</th><td>" + str(entry.get('role', '')) + "</td></tr>"

            if 'content' in entry:
                html_string += "<tr><th>Content</th><td>" + str(entry.get('content', '')) + "</td></tr>"

            if 'name' in entry:
                html_string += "<tr><th>Name</th><td>" + str(entry.get('name', '')) + "</td></tr>"

            if 'function_call' in entry:
                function_call = entry.get('function_call', {})
                html_string += "<tr><th>Function Name</th><td>" + str(function_call.get('name', '')) + "</td></tr>"
                html_string += "<tr><th>Function Arguments</th><td>" + str(function_call.get('arguments', '')) + "</td></tr>"

            if 'function' in entry:
                html_string += "<tr><th>Function</th><td>" + str(entry.get('function', '')) + "</td></tr>"

        html_string += "</table><br>"

    html_string += "</body></html>"
    return html_string

def create_message(original_message, send_subject, send_body, debug_log=None):
    """Create a message for an email."""
    message = MIMEMultipart('alternative')
    message['from'] = 'Customer-service@expo-growth.com'
    message['to'] = original_message['return_path']

    if send_subject:
        message['subject'] = send_subject
    else:
        if original_message['subject'].upper().startswith("RE:"):
            message['subject'] = original_message['subject'] 
        else:
            message['subject'] = "Re: " + original_message['subject']

    if original_message.get('in_reply_to'):
        message['In-Reply-To'] = original_message['in_reply_to']
    if original_message.get('references'):
        message['References'] = original_message['references']

    original_text = original_message['body']
    original_message['body'] = original_message['body'].replace('\n', '<br />')

    body = '<div dir="ltr">' \
        + send_body \
        + '</div><br><br><br>' \
        + '<div class="gmail_quote"><div dir="ltr" class="gmail_attr">' \
        + 'On ' + original_message["original_message_date"] + ' at ' \
        + original_message["original_message_time"] + ' ' + original_message["original_message_from"] \
        + ' wrote:<br></div>' \
        + '<blockquote class="gmail_quote" style="margin:0px 0px 0px 0.8ex;border-left:1px solid rgb(204,204,204);padding-left:1ex">' \
        + original_text \
        + '</div>' \
        + '</blockquote>'
    
    # Adding the debug_log if provided
    if debug_log:
        body += '<br><br>' + json_to_html(debug_log)

    msg = MIMEText(body, 'html')
    message.attach(msg)

    # Adjusted return format for consistency
    return {
        'message': {
            'raw': base64.urlsafe_b64encode(message.as_string().encode()).decode(),
            'thread_id': original_message["thread_id"]
        }
    }


def apply_labels(service, label_name, email_id):
    """Apply the specified labels to a specific email."""

    # remove \ character from the label names
    # label_names = [label_name.replace("\\", "") for label_name in label_names]
    # Fetch the list of existing labels
    results = service.users().labels().list(userId='me').execute()
    existing_labels = results.get('labels', [])

    label_ids_to_apply = []


    label_id = None
    for label in existing_labels:
        if label['name'] == label_name:
            label_id = label['id']
            break

    # If the label doesn't exist, create it
    if label_id is None:
        label_body = {
            'name': label_name
        }
        created_label = service.users().labels().create(userId='me', body=label_body).execute()
        label_id = created_label['id']

    label_ids_to_apply.append(label_id)

    # Apply the labels to the specified email
    applied_labels = service.users().messages().modify(userId='me', id=email_id, body={'addLabelIds': label_ids_to_apply}).execute()

    return applied_labels




def reply_and_label_email(service, id, send_body, debug_log, label_name, mode="debug", send_subject=None):
    """Send an email message."""
    try:
        original_message = get_info_from_id(service, id)

        # alter the data when entering debug mode
        if mode == "debug":
            original_message, label_name, send_subject = debug_alteration(original_message, label_name)
        elif mode == "production":
            debug_log = ""

        send_message = create_message(original_message, send_subject, send_body, debug_log)

        if mode == "debug":
            send_message['referenceId'] = ""
            send_message['In-Reply-To'] = ""
        
        sended_message = service.users().messages().send(userId="me", body=send_message['message']).execute()

        # check if the label_names is not empty, then apply the label
        if label_name:
            applied_label = apply_labels(service, label_name, sended_message['id'])
            print('Applied label: %s' % applied_label['labelIds'][0])

        if mode == "production":
            # remove the specified label after successfully sending the email
            remove_label_from_thread(service, 'Label_1274735915684369724', sended_message['threadId'])
    

        return sended_message
    except Exception as e:
        print("Error sending email:", e)
        return None


def remove_label_from_thread(service, label_id, thread_id):
    """Remove a label from an entire thread."""
    try:
        # Fetch the thread using the thread ID
        thread = service.users().threads().get(userId='me', id=thread_id).execute()
        
        # Extract all message IDs from the thread
        message_ids = [message['id'] for message in thread['messages']]
        
        # For each message ID, remove the label
        for message_id in message_ids:
            service.users().messages().modify(userId="me", id=message_id, body={'removeLabelIds': [label_id]}).execute()
            print(f"Removed label {label_id} from message {message_id}.")
            
    except Exception as e:
        print(f"Error removing label {label_id} from thread {thread_id}: {e}")




def debug_alteration(original_message, label_name):
    """Alter the original message for debugging purposes."""

    # include tag in subject
    label_name_str = str(label_name)
    send_subject = "[" + label_name_str + "]" + " [debug/testing] | " + original_message['subject']

    # delete the tag
    label_name = []

    # change the return path 
    original_message['return_path'] = 'gpt.as.cs.debug@gmail.com'

    return original_message, label_name, send_subject

    

# service = build('gmail', 'v1', credentials=authenticate())
# id = '18b08b895156de40'
# send_subject = ""
# send_body = "<p>Dear Herman Kwok,</p><p>Thank you for reaching out to us. Here are the details of your order:</p><ul><li>Order Number: #SP2-6001</li><li>Order Date: 2023-09-09</li><li>Customer Name: Cindy Chesney</li><li>Shipping Address: Cindy Chesney,15400 Mississippi 15,Decatur, Mississippi 39327,United States</li><li>Item Info: Halloween Flash Sale - Haunted Halloween Projector, 100inch Projector Screen (Halloween Promotion), Quantity: 1</li><li>Fulfilled At: 2023-09-19</li><li>Tracking Number: 4203932792748927005303010268239318</li><li>Tracking URL: <a href='https://t.17track.net/#nums=4203932792748927005303010268239318&fc=190012'>Track your order here</a></li></ul><p>If you have any other questions, feel free to ask.</p><p>Best regards,</p><p>Jason Kwok</p><p>Shoplium Customer Service Team</p>"
# debug_log = ''
# label_names = ['resolved']

# # 2 different modes "debug" and "production"
# mode = "production"


# reply_and_label_email(service, id, send_subject, send_body, debug_log, label_names, mode)



### how to use 

# use reply_and_label_email function
#     - essentials are service, id, send_body,label_names and mode
#     - optional are send_subject and debug_log
#         + send_subject will overide everythign and become the subject of the email
#         + debug_log will add at the end of the email, mostly used for debugging purposes
#     - mode can be "production" or "debug"



import re
from googleapiclient.discovery import build
import base64
from googleapiclient.errors import HttpError
from gmail_api.cs_gmail_cred.cred import *

def extract_bodies(part):
    """Extract and clean email bodies from the email part."""
    bodies = []

    mimeType = part.get('mimeType')
    if mimeType in ['text/plain', 'text/html']:
        data_str = part.get('body', {}).get('data')
        if isinstance(data_str, str):
            try:
                decoded_content = base64.urlsafe_b64decode(data_str).decode('utf-8', 'ignore')
                cleaned_content = refine_email_content(decoded_content)
                bodies.append(cleaned_content)
            except (base64.binascii.Error, UnicodeDecodeError) as e:
                print(f"Error decoding data: {data_str}. Error: {e}")
    elif 'parts' in part:
        # Prioritize 'text/plain' MIME type
        plain_parts = [sp for sp in part['parts'] if sp.get('mimeType') == 'text/plain']
        if plain_parts:
            bodies.extend(extract_bodies(plain_parts[0]))
        else:
            for subpart in part['parts']:
                bodies.extend(extract_bodies(subpart))

    return bodies[:1]


def refine_email_content(body):
    """Clean unwanted patterns from email body."""

    # Remove HTML tags and entities
    body = re.sub(r'<[^>]+>', '', body)
    body = re.sub(r'&[a-z]+;', ' ', body)

    # Remove URLs
    body = re.sub(r'http\S+', '', body)

    # Remove CSS styles, script tags, and the specific #yiv... styles
    body = re.sub(r'<style.*?</style>', '', body, flags=re.DOTALL)
    body = re.sub(r'#\w+ {[^}]+}', '', body)
    body = re.sub(r'#yiv9353888082 \..+?}', '', body, flags=re.DOTALL)
    body = re.sub(r'<script.*?</script>', '', body, flags=re.DOTALL)

    # Remove content between { and }
    body = re.sub(r'\{.*?\}', '', body)

    # Remove email quoted content
    body = re.sub(r'On .* wrote:', '', body)
    body = re.sub(r'---.*?---', '', body)

    # Remove email signatures and footers
    signature_keywords = ["unsubscribe", "To view this discussion on the web visit", "You received this message because", "sent from my"]
    for keyword in signature_keywords:
        body = body.split(keyword, 1)[0]

    # Remove extra whitespaces, newlines and potential marker patterns
    body = ' '.join(body.split())

    return body.strip()


def get_email_metadata(email_message):
    """Extract email metadata from the email message."""
    headers = {header['name']: header['value'] for header in email_message['payload']['headers']}
    headers_lower = {k.lower(): v for k, v in headers.items()}
    return {
        'id': email_message['id'],
        'threadId': email_message['threadId'],
        'name': headers_lower.get('from', '').split('<')[0],
        'Sender': re.search(r'<(.*?)>', headers_lower.get('from', '')).group(1) if '<' in headers_lower.get('from', '') else headers_lower.get('from', ''),
        'return_path': re.search(r'<(.*?)>', headers_lower.get('return-path', '')).group(1) if '<' in headers_lower.get('return-path', '') else headers_lower.get('return-path', ''),
        'recipient': headers_lower.get('to', ''),
        'date': headers_lower.get('date', ''),
        'Subject': headers_lower.get('subject', ''),
        'Tag': email_message['labelIds'],
        'Body': ''
    }

def get_label_ids_for_stores(service, storeIds):
    """Retrieve the label IDs for a given list of store IDs."""
    try:
        labels = service.users().labels().list(userId='me').execute().get('labels', [])
        label_ids = []
        for store_id in storeIds:
            label_id = next((l['id'] for l in labels if l['name'] == store_id), None)
            if not label_id:
                raise ValueError(f"No label found with the name {store_id}.")
            label_ids.append(label_id)
        return label_ids
    except HttpError as e:
        raise ValueError(f"Failed to fetch labels. Error: {e}")

def fetch_threads_by_labels(service, label_ids, max_results):
    """Fetch threads that have all the given label IDs."""
    try:
        thread_list = service.users().threads().list(userId='me', labelIds=label_ids, maxResults=max_results).execute()
        return thread_list.get('threads', [])
    except HttpError as e:
        label_ids_str = ', '.join(label_ids)
        raise ValueError(f"Failed to fetch threads for labels with IDs {label_ids_str}. Error: {e}")

def extract_email_from_thread(service, thread_data):
    """Extract email details from a given thread data."""
    try:
        target_thread = service.users().threads().get(userId='me', id=thread_data['id']).execute()
        messages = target_thread.get('messages', [])
        if not messages:
            raise ValueError(f"Thread with ID {thread_data['id']} doesn't have any messages.")
        
        latest_email_message = messages[-1]
        email_content = get_email_metadata(latest_email_message)
        email_content['Body'] = extract_bodies(latest_email_message['payload'])
        
        return email_content
    except HttpError as e:
        print(f"Failed to fetch thread with ID {thread_data['id']}. Error: {e}")
        return None

def get_emails_from_storeId(service, storeId, max_results):
    """Fetch latest emails from threads based on storeId."""
    # service = build('gmail', 'v1', credentials=authenticate())

    label_with_storeId_need_reply = [storeId , "need-reply"]

    label_id = get_label_ids_for_stores(service, label_with_storeId_need_reply)
    threads = fetch_threads_by_labels(service, label_id, max_results)
    emails = [extract_email_from_thread(service, thread_data) for thread_data in threads]

    return emails




# email_message = latest_email_message
# thread_data = {'id': '18b2b119c027288c', 'snippet': 'Dear Alana Patrick, Thank you for reaching out to us. I see that you ordered the &#39;Halloween Flash Sale - Haunted Halloween Projector&#39; with the &#39;85inch Projector Screen (Halloween Promotion)', 'historyId': '518556'}


import openai

import json

# import my own functions and variables
from gmail_api.read_emails import *
from gmail_api.cs_gmail_cred.cred import *
from gmail_api.reply_and_label_email import *
from gmail_api.draft_and_label_email import *

from shopify_api.order_info_pull import *

from openai_api.system_message_and_functions import *
from openai_api.gpt_setup import *
from openai_api.store_info import *
from openai_api.gpt_make_decision import *

def get_sop_and_customer_order_info(arguemnts_dict):
    gpt_function_call_arguments = arguemnts_dict
    sop_and_customer_order_info = {}

    # Check if the key "get_full_order_info" exists and run the corresponding function
    if "get_full_order_info" in gpt_function_call_arguments:
        sop_and_customer_order_info["Shopify customer and order info"] = get_full_order_info(gpt_function_call_arguments["get_full_order_info"])


    # Check if the key "get_store_info" exists and run the corresponding function
    if "get_store_info" in gpt_function_call_arguments:
        sop_and_customer_order_info["SOP"] = get_store_info(storeId, gpt_function_call_arguments["get_store_info"])

    return sop_and_customer_order_info

def decision_made_with_email_info(arguments_dict):
    # draft_and_label_email(service, id, send_body, debug_log, label_names, send_subject = None, mode = "debug")
    # reply_and_label_email(service, id, send_subject, send_body, debug_log, label_names, mode)
    # service = build('gmail', 'v1', credentials=authenticate())

    # id = target_email["id"]
    # gpt_arguement = json.loads(gpt_decision_output['choices'][0]['message']['function_call']['arguments'])
    # send_subject = gpt_arguement['send_subject']
    # send_body = gpt_arguement['send_body']

    
    # send_body = arguments_dict['send_body']
    # labels_name = arguments_dict['labels_name']

    # print("send_body:", send_body)
    # print("labels_name:", labels_name)

    print("decision_made_with_email_info ran sucessfully")

    
def debug_log_to_html(debug_log):
    formatted_string = '<div dir="ltr">'
    
    for entry in debug_log:
        role = entry.get('role', '').capitalize()
        content = entry.get('content', '')

        if role == "Assistant" or role == "User":
            formatted_string += f"<p><strong>{role}:</strong> {content}</p>"

        if 'function_call' in entry:
            func_name = entry['function_call'].get('name', '')
            args = entry['function_call'].get('arguments', '')
            formatted_string += f"<p><strong>{role} executed function:</strong> {func_name}</p>"
            formatted_string += f"<p>Arguments: {args}</p>"

    formatted_string += '</div>'
    return formatted_string


def send_draft_label_email(service, target_email, decision_made, gpt_response, debug_log, mode):
    debug_log_in_html = debug_log
    
    # Safely parse the JSON and assign default values in case of errors.
    try:
        label_name = json.loads(gpt_response['choices'][0]['message']['function_call']['arguments'])['labels_name'][0]
    except:
        label_name = 'error'
        
    try:
        send_body = json.loads(gpt_response['choices'][0]['message']['function_call']['arguments'])['send_body']
    except:
        send_body = "can't load send_body"

    if decision_made:
        # debug_log_in_html = debug_log_to_html(debug_log)
        
        # If label name is "agent help" or "need guideline", then run draft_and_label_email
        if label_name in ['agent-help', 'need-guideline']:
            if  mode == "debug":
                result_email = reply_and_label_email(service, target_email["id"], send_body, debug_log_in_html, label_name, mode)
                logger.info('Send Message Id: %s' % result_email['id'])
            else:
                result_email = draft_and_label_email(service, target_email["id"], send_body, debug_log_in_html, label_name, mode)
                logger.info('Drafted Message Id: %s' % result_email['id'])
        
        # If label name is "resolved" and "not_yet_resolved", then run reply_and_label_email
        elif label_name in ["gpt-sent", "no-need-to-reply"]:
            result_email = reply_and_label_email(service, target_email["id"], send_body, debug_log_in_html, label_name, mode)
            logger.info('Send Message Id: %s' % result_email['id'])
        else:
            print("label_name is not valid")
    else:
        draft_and_label_email(service, target_email["id"], send_body, debug_log_in_html, label_name, mode)
        print("decision was not made")
        print("debug_log:", debug_log)
        print("gpt_response:", gpt_response)



available_functions = {
    "get_sop_and_customer_order_info": get_sop_and_customer_order_info,
    "decision_made_with_email_info": decision_made_with_email_info
}

storeId = "[SP2]"
max_results = 1
system_messages = get_store_system_messages(storeId)
service = build('gmail', 'v1', credentials=authenticate())

# get email from gmail API
email_storage = get_emails_from_storeId(service, storeId, max_results)

for i in range(len(email_storage)):
    logger.info('start working on email: %s' % email_storage[i]['id'])
    target_email = email_storage[i]

    decision_made, gpt_response, debug_log = gpt_make_decision(target_email, available_functions, system_messages)

    send_draft_label_email(service, target_email, decision_made, gpt_response, debug_log, mode="production")

    logger.info('decision is made? : %s' % decision_made)







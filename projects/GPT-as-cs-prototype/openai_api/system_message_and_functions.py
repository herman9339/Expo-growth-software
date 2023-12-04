



functions = [
    {
        "name": "get_sop_and_customer_order_info",
        "description": "Get SOP and info according to scenario and get basic customer and order info",
        "parameters": {
            "type": "object",
            "properties": {
                "get_store_info": {
                    "type": "string",
                    "enum": [
                        "order status & shipping issue",
                        "order change",
                        "shipping to the wrong address",
                        "package lost",
                        "damaged or defective product",
                        "not satisfied",
                        "no sop, need new sop"
                    ],
                    "description": ("The type of scenario for the latest message from the customer.")
                },
                "get_full_order_info": {
                    "type": "object",
                    "properties": {
                        "order_number": {
                            "type": "string",
                            "description": "The number of the order, for example: #HS3-1234. It is not the name of the customer. Can be None."
                        },
                        "order_email": {
                            "type": "string",
                            "format": "email",
                            "description": "The email associated with the order."
                        }
                    },
                    "required": [],
                    "description": ("Information to fetch full order details from Shopify including tracking number and link."
                                    "can work with only order number or email."
                                    "If both order number and email are None, then ask customer for the order number.")
                }
            },
            "required": []
        }
    },
    {
        "name": "decision_made_with_email_info",
        "description": "this will pass the label name and send body to Gmail API to send or draft email and label them. Only use this when sending or drafting email to customer or there is no need to reply or you need agent help.",
        "parameters": {
            "type": "object",
            "properties": {
                # "send_subject": {
                #     "type": "string",
                #     "description": "leave blank in default unless specify"
                # },
                "send_body": {
                    "type": "string",
                    "description": "The body of the email to be sent."
                },
                "labels_name": {
                    "type": "array",
                    "items": {
                        "type": "string",
                        "enum": ["gpt-sent", "agent-help", "need-guideline", "no-need-to-reply"]
                    },
                    "description": ("'gpt-sent': send email and label them. "
                                    "'no-need-to-reply': label them 'no-need-to-reply' and leave send_body empty. "
                                    "'agent-help': enter the reason for help in send_body and label them 'agent-help'. You can also include a drafted email after the reason for help, so the agent can send it to the customer. "
                                    "'need-guideline': use this when no sop is found and you need to ask for guideline. Label them 'need guideline'. you can also suggest a new sop and a name for the situation in send_body. "
                                    "Can only use one label at a time"
                                    )
                }
            },
            "required": ["labels_name"]
        }
    }
]

stores_info = {
    "[PP1]": {
        "store": "Aeternum Jocale",
        "store website address": "https://aeternum-jewelry.com/",
        "scenarios": {
            "order status & shipping issue": (
                "Update customer with attached order and tracking data. "
                "Provide link for parcel tracking. "
                "Inform: Order will arrive in 5-20 business days."
            ),
            "order change": (
                "Review attached order info. "
                "If not shipped: Inform potential change; if clear change identified, seek human approval. "
                "If shipped: Inform no changes or refunds."
            ),
            "shipping to the wrong address": (
                "Review attached order and tracking data. "
                "If addresses match: Inform already delivered. "
                "If mismatch: Escalate and seek human assistance."
            ),
            "package lost": (
                "Review attached order and tracking data. "
                "If undelivered and stuck for >14 days: Escalate and seek human approval."
            ),
            "damaged or defective product": (
                "Request video/photo evidence from customer. "
                "If evidence provided: Escalate and seek human approval."
            ),
            "not satisfied": (
                "Offer immediate 30% gift card. "
                "Optionally, propose customer-paid return and seek human approval if accepted."
            ),
            "no sop found": "ask for guidance"
        }
    },
    "[SP2]": {
        "store": "Shoplium",
        "store website address": "https://shoplium-shop.com/",
        "system_messages": (
            "you are called Jason kwok being assigned to hadle this email. "
            "Use 'get_sop_and_customer_order_info' for SOPs and order details. "
            "If an email lacks order info, ask for the order number (format: SP2-1234). If it starts differently, seek agent help. "
            "If ready to respond, use 'decision_made_with_email_info'. Apply only one label. "
            "If not a customer inquiry, label as 'no-need-to-reply'. "
            "you have to use function in every response"
            "Respond in HTML format. "
            "Note: The 85-inch Projector Screen (Halloween Promotion) doesn't come with a projector. If only the screen was ordered, use the not satisfied SOP. "
            
        ),
        "scenarios": {
            "order status & shipping issue": (
                "Update customer with attached order and tracking data. "
                "Provide link for parcel tracking. "
                "Inform: Order will arrive in 5-20 business days."
            ),
            "order change": (
                "Review attached order info. "
                "If not shipped: Inform potential change; if clear change identified, label email with agent-help"
                "If shipped: Inform no changes or refunds."
            ),
            "shipping to the wrong address": (
                "Review attached order and tracking data. "
                "If addresses match: Inform already delivered. "
                "If mismatch: Escalate and ask for agent help."
            ),
            "package lost": (
                "Ask for agent help"
            ),
            "damaged or defective product": (
                "Request video/photo evidence from customer. "
                "If evidence provided: ask for agent help."
            ),
            "not satisfied": (
                "Offer immediate 30% gift card. "
                "Optionally, propose customer-paid return. "
                "Only if they have accepted the return, tell them we have already esculated this to my supervisor, they will provide you with the return instruction. Then label this email with agent-help. "
                "also try to comfort them as much as possible"
            ),
            "no sop, need new sop": "ask agent for help"
        }
    }
}

def get_store_info(storeId,scenarios):
    return stores_info[storeId]["scenarios"][scenarios]

def get_store_system_messages(storeId):
    return stores_info[storeId]["system_messages"]

from numpy import append
import shopify
from datetime import datetime


shop_url = "slueone.myshopify.com"
api_version = '2023-04'
private_app_password = "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"



class FullOrderInfo:
    def __init__(self, 
                 order_number: str, 
                 order_date: datetime, 
                 customer_email: str, 
                 customer_name: str, 
                 shipping_address: str, 
                 item_info: dict, 
                 fulfilled_on: datetime = None, 
                 tracking_number: str = None, 
                 tracking_url: str = None):
        
        self.order_number = order_number
        self.order_date = order_date
        self.customer_email = customer_email
        self.customer_name = customer_name
        self.shipping_address = shipping_address
        self.item_info = item_info
        self.fulfilled_on = fulfilled_on
        self.tracking_number = tracking_number
        self.tracking_url = tracking_url

    def __str__(self):
        return f"Order Info:\n" \
               f"Order Name: {self.order_number}\n" \
               f"Order Date: {self.order_date}\n" \
               f"Email: {self.customer_email}\n" \
               f"Customer Name: {self.customer_name}\n" \
               f"Shipping Address: {self.shipping_address}\n" \
               f"Item Info: {self.item_info}\n" \
               f"Fulfilled On: {self.fulfilled_on}\n" \
               f"Tracking Number: {self.tracking_number}\n" \
               f"Tracking url: {self.tracking_url}"

def establish_session(shop_url, api_version, private_app_password):
    session = shopify.Session(shop_url, api_version, private_app_password)
    shopify.ShopifyResource.activate_session(session)

#def a function which find by the order_number
def get_order_id_by_order_number(order_number):
    try:
        order_id = str(shopify.Order.find(name = order_number, status = 'any')).split("(")[1].split(")")[0]
        # order_info = shopify.Order.find(order_id)
        return order_id
    except:
        print(f"get_order_by_order_number not working properly - {order_number}")
        return None


#def a function which find by the customer email
def get_order_id_by_email(order_email):
    try:
        order_id = str(shopify.Order.find(email = order_email, status = 'any')).split("(")[1].split(")")[0]
        # order_info = shopify.Order.find(order_id)
        return order_id
    except:
        print(f"get_order_by_order_order_email not working properly - {order_email}")
        return None

# get customer name from customer ID
def get_customer_name_from_customer_id(customer_id):
    customer = shopify.Customer.find(customer_id)
    customer_name = customer.first_name + " " + customer.last_name
    return customer_name

# get item and quantity from product ID
def get_item_info_from_line_items(line_items):
    item_info = []
    for item in line_items:
        item_detail = {
            "title": item.title,
            "variant_title": item.variant_title,
            "quantity": item.quantity
        }
        item_info.append(item_detail)
    return item_info

# get fulfillment info from fulfillment object
def get_fulfillment_info_from_fulfillment_object(fulfillment_object):
    fulfillment_info = []  # This will hold all fulfillment_info dictionaries

    if not fulfillment_object:
        return {
            "num of package": 0,
            "fulfillments": [{
                "fulfilled at": 'not fulfilled',
                "tracking_number": 'not fulfilled',
                "tracking_url": 'not fulfilled'
            }]
        }

    for fulfillment in fulfillment_object:
        single_fulfillment_info = {
            "fulfilled at": fulfillment.created_at,
            "tracking_number": fulfillment.tracking_number,
            "tracking_url": fulfillment.tracking_url,
        }
        fulfillment_info.append(single_fulfillment_info)

    return {
        "num of package": len(fulfillment_info),
        "fulfillments": fulfillment_info
    }


def get_full_address(shipping_address):
    attributes = shipping_address.attributes

    address_parts = [
        f"{attributes.get('first_name', '')} {attributes.get('last_name', '')}",
        attributes.get('address1', ''),
        attributes.get('address2', '') or '',  # The 'or' ensures that if address2 is None, it will default to an empty string.
        f"{attributes.get('city', '')}, {attributes.get('province', '')} {attributes.get('zip', '')}",
        attributes.get('country', '')
    ]

    # Join the parts into a full address, skipping any empty lines
    return ','.join(part for part in address_parts if part.strip())

# get order info from gpt input
def get_order_info_from_gpt_input(customer_info_from_gpt):
    order_id = None

    # Fetching order_id using order_number
    if customer_info_from_gpt.get('order_number'):
        order_id = get_order_id_by_order_number(customer_info_from_gpt['order_number'])
    
    # If not found using order_number or it was None, try using order_email
    if not order_id and customer_info_from_gpt.get('order_email'):
        order_id = get_order_id_by_email(customer_info_from_gpt['order_email'])

    # If we still can't find the order_id
    if not order_id:
        print("No input or couldn't find the order using given details.")
        return None

    # Fetching order information using order_id
    order_info = shopify.Order.find(order_id)
    if order_info:
        return order_info
    else:
        print(f"Couldn't fetch the order information for order_id: {order_id}")
        return None


def get_full_order_info(customer_info_from_gpt):
    try:
        # 1. Check if both 'order_number' and 'order_email' are None. If yes, raise an error.
        order_number = customer_info_from_gpt.get('order_number')
        order_email = customer_info_from_gpt.get('order_email')
        
        if not order_number and not order_email:
            raise ValueError("Incomplete input data: Missing both 'order_number' and 'order_email'")
        
        # 2. Check for shop_url, api_version, private_app_password
        if not shop_url or not api_version or not private_app_password:
            raise ValueError("Incomplete environment data: Missing shop_url, api_version or private_app_password")
        
        # 3. Establishing session
        establish_session(shop_url, api_version, private_app_password)
        
        # 4. Retrieve order info using the customer_info_from_gpt
        partial_order_info = get_order_info_from_gpt_input(customer_info_from_gpt)
        
        # If order not found, raise error with the custom message
        if not partial_order_info:
            raise ValueError(f"Unable to find the order with the order number {order_number} and email {order_email}. Please ask customer for the correct order number or ordering email.")
        
        # 5. Extracting details and constructing the full order information
        customer_name = get_customer_name_from_customer_id(partial_order_info.customer.id)
        item_info = get_item_info_from_line_items(partial_order_info.line_items)
        fulfillment_info = get_fulfillment_info_from_fulfillment_object(partial_order_info.fulfillments)

        if not fulfillment_info['fulfillments']:
            raise ValueError("No fulfillments available")
        
        full_order_info = {
            'order_number': partial_order_info.name,
            'order_date': partial_order_info.created_at,
            'customer_email': partial_order_info.email,
            'customer_name': customer_name,
            'shipping_address': get_full_address(partial_order_info.shipping_address),
            'item_info': item_info,
            'fulfilled_at': fulfillment_info['fulfillments'][0]['fulfilled at'],
            'tracking_number': fulfillment_info['fulfillments'][0]['tracking_number'],
            'tracking_url': fulfillment_info['fulfillments'][0]['tracking_url']
        }
        shopify.ShopifyResource.clear_session()
        return full_order_info
    except Exception as e:
        print(f"Error encountered: {e}")
        return None




# print(get_full_order_info({"order_number":"sp2-5999", "order_email": None}))

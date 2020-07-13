import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

# This module sends email when the order status changes.

def format_order_info(order):
  # This function takes in a order row and convert the info into a human-friendly string.
  product_name=order['product']['name']
  created=str(order['created'])
  status=order['status']['status']
  if order['team_purchase'] is not None:
    price=str(order['product']['price_team'])
  else:
    price=str(order['product']['price_single'])
    
  message='''
            <h1>Here is the summary of your recent order on Bazari:</h1>
            <ul>
              <li>Product: {0}</li>
              <li>Price: {1} MXN</li>
              <li>Ordered at: {2}</li>
              <li>Status: {3}</li>
            </ul>
            <p>Check your "Mis ordenes" page in the Bazari app to review the full details.</p>
         '''
  formatted_message=message.format(product_name, price, created, status)
  
  return formatted_message

@anvil.server.callable
def send_email_for_new_order(address, order):
    anvil.email.send(
      from_name="Bazari",
      from_address="operation@bazari.mx",
      to=address,
      subject="Your order confirmation ID: " + str(order['order_id']),
      html=format_order_info(order)
    )

@anvil.server.callable
def send_email_for_order_cancellation_request(address, order):
    anvil.email.send(
      from_name="Bazari",
      from_address="operation@bazari.mx",
      to=address,
      subject="Your order cancellation request ID: " + str(order['order_id']),
      html=format_order_info(order)
    )  
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

from datetime import datetime, timezone
from . import user_management
from . import sending_email
import uuid
from . import user_management

@anvil.server.callable
def create_pending_order(new_order, verify_user_permission=True):
  if verify_user_permission:
    user_management.verify_user_permission(new_order['user'])
  
  order=app_tables.pending_orders.add_row(
    order_id=str(uuid.uuid44()),
    created=datetime.now(timezone.utc),
    status=app_tables.order_statuses.get(status='Esperando ser confirmado'),
    completed=None,
    canceled=None,
    returned=None,
    **new_order
  )
  
  user_copy=dict(list(new_order['user']))
  if user_copy['pending_order']:
    user_copy['pending_order'].append(order)
  else:
    user_copy['pending_order']=[order]
  user_management.update_user(new_order['user'], user_copy)
  
  # Send emails to the customer.
  sending_email.send_email_for_new_order(new_order['user']['email'], order)
  
  return order

# This method gives all  orders of a particular user.
@anvil.server.callable
def get_all_orders_time_sorted(user):
  user_management.verify_user_permission(user)

  orders=app_tables.pending_orders.search(
    tables.order_by("created", ascending=False),
    user=user
  )
  if len(orders) is not 0:
    return orders
  
# This method gives all pending orders (not completed, not returned) of a particular user.
@anvil.server.callable
def get_all_pending_orders_time_sorted(user):
  user_management.verify_user_permission(user)

  orders=app_tables.pending_orders.search(
    tables.order_by("created", ascending=False),
    user=user,
    completed=None,
    canceled=None,
    returned=None
  )
  if len(orders) is not 0:
    return orders

# This method gives all pending orders (not completed, not returned) of a particular user.
@anvil.server.callable
def get_all_completed_orders_time_sorted(user):
  user_management.verify_user_permission(user)
  
  orders=app_tables.pending_orders.search(
    tables.order_by("created", ascending=False),
    user=user,
    status=app_tables.order_statuses.get(status='Completado'),
    canceled=None,
    returned=None
  )
  if len(orders) is not 0:
    return orders
  
@anvil.server.callable
def request_order_cancellation(order):
  user_management.verify_user_permission(order['user'])
  
  order_copy=dict(list(order))
  order_copy['cancellation_requested']=datetime.now(timezone.utc)
  order_copy['status']=app_tables.order_statuses.get(status='Cancelación solicitada')
  order.update(**order_copy)

  # Send emails to the customer.
  sending_email.send_email_for_order_cancellation_request(order['user']['email'], order)
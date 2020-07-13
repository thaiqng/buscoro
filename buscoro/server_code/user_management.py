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

@anvil.server.callable
def update_user(user, user_copy):
  # Check that the user given is really a row in the ‘users’ table.
  if app_tables.users.has_row(user):
    user_copy['updated']=datetime.now(timezone.utc)
    user.update(**user_copy)
  else:
    raise Exception ("User does not exist.")
    
@anvil.server.callable
def get_user_teams_and_orders(user):
  # Check that the user given is really a row in the ‘users’ table.
  if app_tables.users.has_row(user):
    if user['pending_team'] is None:
      user['pending_team']=[]
    if user['pending_order'] is None:
      user['pending_order']=[]
      
    return {
      'pending_team': list(filter(
        lambda team: team['defunct'] is None, user['pending_team']
      )),
      'pending_order': list(filter(
        lambda order: order['completed'] is None, user['pending_order']
      )),
      'completed_order': list(filter(
        lambda order: order['completed'] is not None, user['pending_order']
      ))
    }
  else:
    raise Exception ("User does not exist.")
    
def verify_user_permission(user):
  current_user=anvil.users.get_user()
  if user != current_user:
    raise Exception("You do not have access to these orders.")

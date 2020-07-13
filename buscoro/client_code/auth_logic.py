import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from . import server
from . import nav_logic
    
def check_can_order():
  print('check can order')
  user=server.get_user()
  can_order={
    'signed_in': False,
    'info_completed': False
  }
  
  # Check if user is signed in; if not requires signing in to order.
  if user:
    can_order['signed_in']=True
    
    # Check if user has all the information to order
    profile_completed=check_missing_user_info(user)
    if profile_completed:
      can_order['info_completed']=True
    else:
      anvil.Notification("Please complete your information to create an order.", timeout=5).show()
      nav_logic.go_to_my_profile()
  else:
    anvil.Notification("Please sign in to create an order.", timeout=3).show()

  return can_order

def check_missing_user_info(user):
  print('check missing user info')
  # Check that the user given is really a row in the ‘users’ table
  if app_tables.users.has_row(user):
    name=user['name']
    phone=user['phone']
    address=user['address']
    profile=user['profile_picture']
    
    # Check if user has uploaded a profile picture, if not set the default profile picture.
    if profile is None:
      default_profile(user)
    
    # If the user has their name, phone, and address, he/she can make an order.
    if name and phone and address:
      return True
    else:
      return False
  else:
    anvil.Notification("User does not exist.", timeout=3).show()
    
# This function sets the default profile picture if user hasn't uploaded the profile picture.
def default_profile(user):
  # Initialize a copy of user to store new user input.
  user_copy=dict(list(user))
  user_copy['profile_picture']=anvil.URLMedia("https://res.cloudinary.com/teepublic/image/private/s--1K1z6ZkG--/t_Preview/b_rgb:8bc0d0,c_limit,f_jpg,h_630,q_90,w_630/v1517191886/production/designs/2317478_0.jpg")
  server.update_user(user, user_copy)
  
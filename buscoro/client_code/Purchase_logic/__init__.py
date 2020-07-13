import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import auth_logic
from .. import server
from .Buy_single_confimration import Buy_single_confimration
from .Buy_team_confirmation import Buy_team_confirmation
from .Buy_team_confirmation.Create_team import Create_team
from .Join_private_team import Join_private_team
from .Join_team_confirmation import Join_team_confirmation

# This package contains the purchase logic.

# Buy single function.
def buy_single(product):
  # Check if user is signed in and has the info filled out. Only allow to join team if both conditions are satisfied.    
  can_order=auth_logic.check_can_order()
  signed_in=can_order['signed_in']
  info_completed=can_order['info_completed']
  
  # If the user is not signed in, simply requires him/her to sign in and reopen the form
  if signed_in and info_completed:  
    # Initialize single order.
    new_order={
      'user': server.get_user(),
      'product': product,
      'team_purchase': None
    }
  
    # Open order confirmation.
    order=anvil.alert(
      content=Buy_single_confimration(item=product),
      title="Comprar solo", 
      buttons=[("COMPRAR", True), ("AHORA NO", False)],
      dismissible=False
    )
    
    # If user confirms order, create a new order.
    if order:
      server.create_pending_order(new_order)
      anvil.Notification("You have successfully ordered. Please check Mis pedidos to review your order.", timeout=3).show()
  
  elif signed_in is False:
    anvil.users.login_with_form(allow_cancel=True)
    if anvil.users.get_user(): buy_single(product)
    
# Create team function.
def create_team(product):
  # Check if user is signed in and has the info filled out. Only allow to join team if both conditions are satisfied.
  can_order=auth_logic.check_can_order()
  signed_in=can_order['signed_in']
  info_completed=can_order['info_completed']
  
  # If the user is not signed in, simply requires him/her to sign in and reopen the form
  if signed_in and info_completed: 
    create=anvil.alert(
      content=Buy_team_confirmation(item=product),
      title="Comprar con un amigo", 
      buttons=[("CREAR UN EQUIPO", True), ("AHORA NO", False)],
      dismissible=False
    )

    # Create a new team.
    if create:
      # Initialize new team.
      new_team={
        'creator': anvil.users.get_user(),
        'product': product,
      }
      
      # Create a new team and display the team info.
      created_team=server.create_team(new_team)
      anvil.alert(
        content=Create_team(item=created_team),
        title="Crear un equipo",
        large=True
      )
      
  elif signed_in is False:
    anvil.users.login_with_form(allow_cancel=True)
    if anvil.users.get_user(): created_team(product)
      
# Join private team function for user with a team code.
def join_private_team(member, code=None):
  # Check if user is signed in and has the info filled out. Only allow to join team if both conditions are satisfied.
  can_order=auth_logic.check_can_order()
  signed_in=can_order['signed_in']
  info_completed=can_order['info_completed']
  
  # If the user is not signed in, simply requires him/her to sign in and reopen the form.
  if signed_in and info_completed:
    # This is in case if the user exist the team form.
    completed_team={}
    
    # User can either user the direct link (with URL hash) or input team code to join team.
    if code is None:
      # Input team code and bind it to an empty team object.
      team={}
      join=anvil.alert(
        content=Join_private_team(item=team),
        title="Tengo un equipo",
        buttons=[("UNIRSE A ESTE EQUIPO", True), ("NO TENGO UN EQUIPO", False)]
      )
      
      # If user clicks Join button.
      if join:
        # Get team by team code.
        completed_team=server.get_team_by_team_code(team['code'])
    else:
      completed_team=server.get_team_by_team_code(code)
        
    # Check if there is a team with the currrent code.
    if completed_team is None:
      anvil.Notification("This team doesn't exist. Please re-enter the right team code.", timeout=3).show()
    
    # This is in case if the user exit the Join_private_team form.
    elif completed_team=={}:
      pass
    
    # Carry on to create team orders.
    else:
      # Don't allow user to join his/her own team.
      if completed_team['creator']==member:
        anvil.Notification("You cannot join your own team!", timeout=3).show()
      else:
        create_team_orders(completed_team, member)
        
  elif signed_in is False:
    anvil.users.login_with_form(allow_cancel=True)
    if server.get_user():
      url_hash=anvil.get_url_hash()
      if url_hash:
        join_private_team(member, code=url_hash['code'])
      else:
        join_private_team(member, code=None)
      
# Join public team function.
def join_public_team(public_team, member):
  print('join team')
  # Check if user is signed in and has the info filled out. Only allow to join team if both conditions are satisfied.
  can_order=auth_logic.check_can_order()
  signed_in=can_order['signed_in']
  info_completed=can_order['info_completed']
  
  # If the user is not signed in, simply requires him/her to sign in and reopen the form
  if signed_in and info_completed:
    # Don't allow user to join his/her own team.
    if public_team['creator']==member:
      anvil.Notification("You cannot join your own team!", timeout=3).show()
    else:
      return create_team_orders(public_team, member)

  elif signed_in is False:
    anvil.users.login_with_form(allow_cancel=True)
    if server.get_user(): join_public_team(public_team, member)
            
# This is the function to create two orders, each for each team member.
def create_team_orders(team, member):
  print('create order')
  # Check if the team is already defunct (expired or realized). If it is user cannot join (hence modify) defunct team.
  if team['defunct'] is not None:
    anvil.Notification("This team is no longer available.", timeout=3).show()
  else:
    # Initialize team orders. 
    new_order_creator={
      'user': team['creator'],
      'product': team['product'],
      'team_purchase': team,
    }
    new_order_member={
      'user': member,
      'product': team['product'],
      'team_purchase': team,
    }
    
    # Make a copy of the new team.
    team_copy=dict(list(team))
    team_copy['member']=member
    
    # Serve a form to confirm order.        
    confirm_join=anvil.alert(
      content=Join_team_confirmation(item=team),
      title="Confirmar su equipo",
      large=True,
      buttons=[("UNIRSE A ESTE EQUIPO", True), ("AHORA NO", False)],
      dismissible=False
    )
    
    # If confirm to join the team, update the team, create two orders each for each member of the team.
    if confirm_join:
      server.realize_team(team, team_copy)
      server.create_pending_order(new_order_member)
      server.create_pending_order(new_order_creator, refresh=False, verify_user_persission=False)
      anvil.Notification("You have successfully ordered. Please check Mis pedidos to review your order.", timeout=3).show()
      return True
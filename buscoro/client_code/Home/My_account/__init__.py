from ._anvil_designer import My_accountTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import Purchase_logic
from ... import nav_logic
from ... import server
from ... import auth_logic

class My_account(My_accountTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.   
    self.item=server.get_user()
    
    # Bind profile picture. If there is no profile picture, set the default profile picture once.
    if self.item['profile_picture']:
      self.image_profile.source=self.item['profile_picture']  
    else:
      self.image_profile.source=anvil.URLMedia("https://res.cloudinary.com/teepublic/image/private/s--1K1z6ZkG--/t_Preview/b_rgb:8bc0d0,c_limit,f_jpg,h_630,q_90,w_630/v1517191886/production/designs/2317478_0.jpg")
      auth_logic.default_profile(self.item)
      
  # My profile and my orders links.    
  def button_my_account_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.origin='My_account'
    nav_logic.go_to_my_profile()
    
  def button_my_orders_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.origin='My_account'
    nav_logic.go_to_my_orders()
    
  # Close session and change password links.      
  def link_change_password_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Reset password option. Serve a form to confirm.
    reset_password=alert(
      content="We will send reset password instruction to the email you used to sign up on bazari.",
      title="Reset password",
      buttons=[("RESET", True), ("NO", False)]
    )
    
    # If user confirms to reset password, send him/her the reset password email.
    if reset_password:
      server.reset_password(self.item['email'])
      alert("Reset password instruction has been sent to the email you used to sign up on bazari")

  def link_close_session_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Sign out option. Serve a form to confirm.
    sign_out=alert(
      content="Do you want to sign out of the current session?",
      title="Sign out",
      buttons=[("CERRAR SESSION", True), ("AHORA NO", False)]
    )
    
    # If user confirms to sign out, sign him/her out and redirect to the Explore_products page.
    if sign_out:
      server.sign_out()
      nav_logic.go_to_explore_products()

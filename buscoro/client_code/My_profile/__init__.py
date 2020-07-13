from ._anvil_designer import My_profileTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .My_address_edit import My_address_edit
from .My_info_edit import My_info_edit
from .. import server
from .. import nav_logic

class My_profile(My_profileTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.user = dict(list(server.get_user()))
    self.item = self.user
    
  # This function update the profile UI when the user uploads a profile picture.
  def file_loader_profile_change(self, file, **event_args):
    """This method is called when a new file is loaded into this FileLoader"""
    # Validate if file is .png or .jpg
    if file.content_type is 'image/jpeg' or file.content_type is 'image/png':
      self.image_profile.source=file
      anvil.Notification("Cambiar perfil con éxito.", timeout=3).show()
      
      # Upload user profile picture.
      user_copy=self.user
      user_copy['profile_picture']=file
      server.update_user(user_copy)
    else:
      anvil.Notification("Solo puedes subir una imagen .jpg o .png.", timeout=3).show()

  def link_my_info_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Initialize a copy of user to store new user input.
    user_copy=self.user
    user_copy['name']=self.item['name']
    user_copy['phone']=self.item['phone']
    
    # Open edit form.
    save=alert(
      content=My_info_edit(item=user_copy),
      title="Editar mi informacion", 
      buttons=[("GUARDAR", True), ("CANCELAR", False)]
    )
    
    # If user clicks save, update the user info.
    if save:
      server.update_user(user_copy)
      self.item=server.get_user()
      self.refresh_data_bindings()
    
  def link_my_direction_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Initialize a copy of user to store new user input
    user_copy=self.user
    
    # For user just sign up with no address object, initiate the address object.
    if self.item['address']:
      user_copy['address']=self.item['address']
    else:
      user_copy['address']={
        'street': "",
        'colony': "",
        'city': "",
        'state': "",
        'zip': ""
      }
    
    # Open edit form
    save=alert(
      content=My_address_edit(item=user_copy),
      title="Editar mi direccion", 
      buttons=[("GUARDAR", True), ("CANCELAR", False)]
    )
    
    # If user clicks save, update the user address.
    if save:
      server.update_user(user_copy)
      self.item=server.get_user()
      self.refresh_data_bindings(self.label_my_address.text)

  def link_back_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.go_back()

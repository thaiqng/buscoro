from ._anvil_designer import Product_picture_cardTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Product_picture_card(Product_picture_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # When event 'x-show' is raised, call show_picture.
    self.set_event_handler('x-show', self.show_picture)
    
  # Define the handler function with tag is the order to displayed (defined in the DB) and an extra argument passed from the parent.
  def show_picture(self, show, **event_args):
    if self.tag==show:
      self.visible=True
    else:
      self.visible=False
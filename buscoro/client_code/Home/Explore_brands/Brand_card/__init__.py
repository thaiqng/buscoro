from ._anvil_designer import Brand_cardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import nav_logic

class Brand_card(Brand_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def link_go_to_store_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.origin='Explore_brands'
    nav_logic.go_to_brand_page(self.link_go_to_store.tag)

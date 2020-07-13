from ._anvil_designer import Brand_product_cardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import nav_logic

class Brand_product_card(Brand_product_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def link_detail_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.temporary='brand'
    nav_logic.identifier=self.item['brand']['code_name']
    nav_logic.go_to_product_info(self.item['sku'])

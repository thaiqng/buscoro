from ._anvil_designer import Product_card_verticalTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .... import nav_logic

class Product_card_vertical(Product_card_verticalTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def link_detail_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.origin='Explore_products'
    nav_logic.go_to_product_info(self.item['sku'])

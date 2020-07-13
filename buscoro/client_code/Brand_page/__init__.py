from ._anvil_designer import Brand_pageTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import server
from .. import nav_logic

class Brand_page(Brand_pageTemplate):
  def __init__(self, code_name, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.  
    # Get brand row by given code name and bind it to the form.
    self.item=server.get_brand_by_code_name(code_name, nav_logic.current_category)
    
    # Bind the brand products to the repeating panel
    all_products=self.item['product']
    self.repeating_panel_brand_product_a.items=all_products[0::2]
    self.repeating_panel_brand_product_b.items=all_products[1::2]

  # Back button in Brand_page always leads back to the Explore_brand (not Product_info)  
  def link_back_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.go_back()
    nav_logic.temporary=False

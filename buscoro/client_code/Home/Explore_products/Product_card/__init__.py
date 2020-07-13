from ._anvil_designer import Product_cardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import random

from .... import nav_logic
from .... import server

class Product_card(Product_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    random_1=random.randrange(0,100)
    random_2=random.randrange(0,100)
    self.image_profile_a.source=anvil.URLMedia('https://picsum.photos/id/{}/50'.format(random_1))
    self.image_profile_b.source=anvil.URLMedia('https://picsum.photos/id/{}/50'.format(random_2))
        
  def link_product_details_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.origin='Explore_products'
    nav_logic.go_to_product_info(self.item['sku'])
 
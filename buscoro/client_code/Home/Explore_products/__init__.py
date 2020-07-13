from ._anvil_designer import Explore_productsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import server
from ... import nav_logic

class Explore_products(Explore_productsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)
    
    # Any code you write here will run when the form opens.
    category=list(filter(
      lambda category: category['category_name'] is nav_logic.current_category, server.get_all_categories()
    ))
    self.label_current_category.text=category[0]['spanish_name']
      
    # Get all products having the given category and bind them to the product repeating panels.
    all_products=server.get_all_products_by_category(nav_logic.current_category)
    
    # The first 5 items are spotlights.
    self.repeating_panel_deal.items=all_products[0:5:1]

    # If there are more than 5 items display the "More" section.
    if len(all_products) > 5:
      self.label_more.visible=True
      self.repeating_panel_vertical_a.items=all_products[5::2]
      self.repeating_panel_vertical_b.items=all_products[6::2]      
    else:
      self.label_more.visible=False

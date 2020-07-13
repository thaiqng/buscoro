from ._anvil_designer import Explore_brandsTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import server
from ... import nav_logic
from ... import Purchase_logic

class Explore_brands(Explore_brandsTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.           
    category=list(filter(
      lambda category: category['category_name'] is nav_logic.current_category, server.get_all_categories()
    ))
    
    # Bind category Spanish name to the label. If the category is "Ofertas" change this to "Todas las marcas"
    if nav_logic.current_category is 'hot':
      self.label_current_category.text="TODAS LAS MARCAS"
    else:
      self.label_current_category.text=category[0]['spanish_name']
    
    # Get all brands having the given category and bind them to the product repeating panel.
    all_brands=server.get_all_brands_by_category(nav_logic.current_category)
    self.repeating_panel_brand_a.items=all_brands[0::2]
    self.repeating_panel_brand_b.items=all_brands[1::2]

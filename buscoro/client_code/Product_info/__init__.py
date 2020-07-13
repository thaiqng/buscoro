from ._anvil_designer import Product_infoTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import auth_logic
from .. import Purchase_logic
from .. import nav_logic
from .. import server

class Product_info(Product_infoTemplate):
  def __init__(self, sku, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.    
    # Get the product by sku.
    self.item=server.get_product_by_sku(sku, nav_logic.current_category)
    
    # Get all existing teams for this product and bind them to the repeating panel.
    unrealized_teams=server.get_all_unrealized_public_teams_by_product(self.item)
    
    # If there is any unrealized team, display the list of team(s). Else, display the notice that there is no existing team.
    if unrealized_teams:
      self.label_existing_team.text="Hay "+str(len(unrealized_teams))+" personas esperando para formar un equipo."
      self.repeating_panel_existing_team.visible=True
      self.repeating_panel_existing_team.items=unrealized_teams
    else:
      self.label_existing_team.text="No hay persona que desea formar un equipo ahora."
      self.repeating_panel_existing_team.visible=False
    
    # Get product pictures.
    self.repeating_panel_picture.items=self.item['picture']
    
    # Initialize picture carousel.
    self.picture_visible=1
    self.repeating_panel_picture.raise_event_on_children('x-show', show=self.picture_visible)
    self.display_carousel_nav_links()

  # Next and previous links for the carousel.
  def link_next_picture_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.picture_visible+=1
    self.repeating_panel_picture.raise_event_on_children('x-show', show=self.picture_visible)
    self.display_carousel_nav_links()
      
  def link_previous_picture_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.picture_visible-=1
    self.repeating_panel_picture.raise_event_on_children('x-show', show=self.picture_visible)
    self.display_carousel_nav_links()
      
  # Display next and previous links logic.
  def display_carousel_nav_links(self):
    number_of_pictures=len(self.repeating_panel_picture.items)

    if self.picture_visible is 1:
      self.link_previous_picture.visible=False
    else:
      self.link_previous_picture.visible=True      
      
    if self.picture_visible is number_of_pictures:
      self.link_next_picture.visible=False
    else:
      self.link_next_picture.visible=True      
  
  # Buy links.
  def link_buy_single_click(self, **event_args):
    """This method is called when the button is clicked"""
    Purchase_logic.buy_single(self.item)

  def link_buy_team_click(self, **event_args):
    """This method is called when the button is clicked"""
    Purchase_logic.create_team(self.item)

  # Go back link.
  def link_back_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.go_back()
    nav_logic.temporary=False

  # Go to brand page link.
  def link_brand_click(self, **event_args):
    """This method is called when the link is clicked"""
    nav_logic.temporary='product'
    nav_logic.identifier=self.item['sku']
    nav_logic.go_to_brand_page(self.item['brand']['code_name'])
  
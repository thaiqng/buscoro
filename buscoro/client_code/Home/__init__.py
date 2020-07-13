from ._anvil_designer import HomeTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import Purchase_logic
from .. import nav_logic
from .. import server

from .Explore_brands import Explore_brands
from .Explore_products import Explore_products
from .My_account import My_account

class Home(HomeTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    nav_logic.form=self
    if nav_logic.content is None:
      self.show_product(nav_logic.current_category)
  
  # The UI bit: makes the link looks selected to indicate the current location.
  # Highlight the current content in the side bar and the top bar.
  def content_highlight(self):
      # Product links.
      self.link_explore_products.foreground='#FF164E' if nav_logic.content_name is "product" else '#666666'
      self.link_explore_products_copy.text='         ' if nav_logic.content_name is "product" else '   '
      self.link_explore_products_copy.align='right' if nav_logic.content_name is "product" else 'left'
      self.link_explore_products_copy.underline=True if nav_logic.content_name is "product" else False
      self.link_explore_products_copy.foreground='#FFFFFF'
      self.link_explore_products_copy.icon_align='top' if nav_logic.content_name is "product" else 'right_edge'
      
      # Brank links.
      self.link_explore_brands.foreground='#FF164E' if nav_logic.content_name is "brand" else '#666666'
      self.link_explore_brands_copy.text='         ' if nav_logic.content_name is "brand" else '   '
      self.link_explore_brands_copy.align='right' if nav_logic.content_name is "brand" else 'left'
      self.link_explore_brands_copy.underline=True if nav_logic.content_name is "brand" else False
      self.link_explore_brands_copy.foreground='#FFFFFF'
      self.link_explore_brands_copy.icon_align='top' if nav_logic.content_name is "brand" else 'right_edge'    
      
      # Account links
      self.link_my_account.foreground='#FF164E' if nav_logic.content_name is "account" else '#666666'
      self.link_my_account_copy.text='         ' if nav_logic.content_name is "account" else '   '
      self.link_my_account_copy.align='right' if nav_logic.content_name is "account" else 'left'
      self.link_my_account_copy.underline=True if nav_logic.content_name is "account" else False
      self.link_my_account_copy.foreground='#FFFFFF'
      self.link_my_account_copy.icon_align='top' if nav_logic.content_name is "account" else 'right_edge'
      
   # Highlight the current category in the side bar.
  def category_highlight(self):
    self.link_category_hot.foreground='#FF164E' if nav_logic.current_category is 'hot' else '#666666'
    self.link_category_super.foreground='#FF164E' if nav_logic.current_category is 'supermarket' else '#666666'
    self.link_category_fashion.foreground='#FF164E' if nav_logic.current_category is 'fashion' else '#666666'
    self.link_category_beauty.foreground='#FF164E' if nav_logic.current_category is 'beauty' else '#666666'
    self.link_category_tech.foreground='#FF164E' if nav_logic.current_category is 'tech' else '#666666'
    
  # Reusable function to show products.
  def show_product(self, show_category):
    nav_logic.current_category=show_category
    nav_logic.content=Explore_products()
    nav_logic.load_explore_products()
    
  # Reusable function to show brands.
  def show_brand(self, show_category):
    nav_logic.current_category=show_category
    nav_logic.content=Explore_brands()
    nav_logic.load_explore_brands()

  # Clear and load the content given the form.
  def load_content(self, content):
    content.remove_from_parent()
    self.column_panel_main_content.clear()
    self.column_panel_main_content.add_component(content)
  
  # Side navigation links.
  def link_explore_products_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.show_product('hot')
  
  def link_explore_brands_click(self, **event_args):
    """This method is called when the button is clicked"""
    self.show_brand('hot')

  def link_my_account_click(self, **event_args):
    """This method is called when the button is clicked"""
    nav_logic.content=My_account()
    nav_logic.load_my_account()

  # Top navigation links. Simply call the corresponding side navigation event.
  def link_explore_products_copy_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.link_explore_products_click()

  def link_explore_brands_copy_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.link_explore_brands_click()
    
  def link_my_account_copy_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.link_my_account_click()
    
  # Category selection links. This section is implemented in the front-end to increase performance. 
  def link_category_hot_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.show_brand('hot') if nav_logic.content_name is "brand" else self.show_product('hot')

  def link_category_super_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.show_brand('supermarket') if nav_logic.content_name is "brand" else self.show_product('supermarket')
      
  def link_category_fashion_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.show_brand('fashion') if nav_logic.content_name is "brand" else self.show_product('fashion')
 
  def link_category_beauty_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.show_brand('beauty') if nav_logic.content_name is "brand" else self.show_product('beauty')

  def link_category_tech_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.show_brand('tech') if nav_logic.content_name is "brand" else self.show_product('tech')
 
  # Expand and collapse the pages and categories sections.
  def link_navigation_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.link_navigation.icon is "fa:caret-down":
      self.link_navigation.icon="fa:caret-up"
      self.column_panel_navigation.visible=True
    elif self.link_navigation.icon is "fa:caret-up":
      self.link_navigation.icon="fa:caret-down"
      self.column_panel_navigation.visible=False

      
  # Have team link.
  def link_have_team_click(self, **event_args):
    """This method is called when the button is clicked"""
    Purchase_logic.join_private_team(server.get_user())

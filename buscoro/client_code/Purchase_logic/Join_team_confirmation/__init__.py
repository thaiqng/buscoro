from ._anvil_designer import Join_team_confirmationTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.server
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

class Join_team_confirmation(Join_team_confirmationTemplate):
  def __init__(self, **properties):
    print("join team confirmation")
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.        
    # Get product pictures.
    self.repeating_panel_picture.items=self.item['product']['picture']
    
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
  
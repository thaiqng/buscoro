from ._anvil_designer import My_ordersTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from .. import server
from .. import nav_logic

class My_orders(My_ordersTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    # Get the pending teams, pending orders, and completed orders.
    self.pending_teams=server.get_all_pending_teams_by_creator()
    self.pending_orders=server.get_all_pending_orders()
    self.completed_orders=server.get_all_completed_orders()

    # The initial view is the pending order view.
    self.get_content="pending"
    self.link_get_content_click()
    
  # Display team repeating panel logic.
  def display_team(self, teams):    
    # If there is at least one team, display the repeating panel with content.
    if teams:
      self.repeating_panel_pending_team.visible=True
      self.label_no_team.visible=False
      self.repeating_panel_pending_team.items=teams

    # Display message if there is no team.
    else:
      self.repeating_panel_pending_team.visible=False
      self.label_no_team.visible=True    

  # Display order repeating panel logic.
  def display_order(self, orders):    
    # If there is at least one order, display the repeating panel with content.
    if orders:
      self.repeating_panel_order.visible=True
      self.label_no_order.visible=False
      self.repeating_panel_order.items=orders

    # Display message if there is no order.
    else:
      self.repeating_panel_order.visible=False
      self.label_no_order.visible=True 
      
  def link_get_content_click(self, **event_args):
    """This method is called when the link is clicked"""
    self.repeating_panel_order.raise_event_on_children('x-content', content=self.get_content)

    if self.get_content is "pending":
      # Change the navigation route and the change view link.
      self.link_back.text="Mi cuenta > Mis pedidos pedientes"
      self.link_get_content.text="Ver mis pedidos completados"
      
      # Show the pending team title.
      self.label_pending_team.visible=True
    
      # Change the order labels and the repeating panel content.
      self.label_order.text="Mis pedidos pendientes"
      self.label_no_order.text="No tiene ningún pedido pendiente."
      
      # Content logic.
      self.display_team(self.pending_teams)
      self.display_order(self.pending_orders)

      # Reset the next content to get.
      self.get_content="completed"
      
    elif self.get_content is "completed":
      # Change the navigation route and the change view link.
      self.link_back.text="Mi cuenta > Mis pedidos completados"
      self.link_get_content.text="Ver mis pedidos pendientes"
      
      # Hide the entire pending team section.
      self.label_pending_team.visible=False
      self.label_no_team.visible=False
      self.repeating_panel_pending_team.visible=False
      
      # Change the order labels and the repeating panel content.
      self.label_order.text="Mis pedidos completados"
      self.label_no_order.text="No tiene ningún pedido completado."
      
      # Content logic.
      self.display_order(self.completed_orders)
      
      # Reset the next content to get.
      self.get_content="pending"

  def link_back_click(self, **event_args):
    """This method is called when the link is clicked"""
    nav_logic.go_back()

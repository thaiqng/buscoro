from ._anvil_designer import My_order_cardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.server
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import server
from ... import nav_logic

class My_order_card(My_order_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.set_event_handler('x-content', self.origin_content)
    
    # Display the status of the order.
    self.status=self.item['status']['status']

    # Select the right price to display depending if the order is with team purchase or single purchase.
    if self.item['team_purchase'] is not None:
      self.label_cost.text="Precio: $"+str(self.item['team_purchase']['product']['price_team'])
    else: 
      self.label_cost.text="Precio: $"+str(self.item['product']['price_single'])

    # Initialize the card.
    self.origin="pending"

  # Set the origin of the cancel button.
  def origin_content(self, content, **event_args):
    self.origin=content
  
  def link_product_click(self, **event_args):
    """This method is called when the link is clicked"""
    nav_logic.origin='My_orders'
    nav_logic.go_to_product_info(self.item['product']['sku'])

  def link_hide_click(self, **event_args):
    """This method is called when the link is clicked"""
    if self.link_hide.text is "MOSTRAR":
      self.column_panel_detail.visible=True
      self.link_hide.text="OCULTAR"
    elif self.link_hide.text is "OCULTAR":
      self.column_panel_detail.visible=False
      self.link_hide.text="MOSTRAR"
      
  def button_cancel_order_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Option to cancel order. If the order is already (requested) cancelled then nothing happens.
    if self.status=="Cancelación solicitada" or self.status=="Cancelación aceptada" or self.status=="Cancelado":
      alert("El cancelación ha sido procesado")
    else:
      # Create a copy of the requested cancellation order and serve a confirmation form.
      if self.origin is "pending":
        cancel = alert(
          content="Bla bla cancel pending order",
          title="Cancelar este pedido", 
          buttons=[("SI, CANCELAR", True), ("AHORA NO", False)]
        )
      elif self.origin is "completed":
        cancel = alert(
          content="Bla bla return completed order",
          title="Solicitar devolucion", 
          buttons=[("SI, SOLICITAR", True), ("AHORA NO", False)]        
        )

      # If user confirms to cancel, change the order status and send him/her an email.
      if cancel:
        server.request_order_cancellation(self.item)
        alert("Your order cancel request has been received. We will inform you with the cancellation status through Facebook Messenger.")
        self.label_status_value.text="Cancelación solicitada"
        self.refresh_data_bindings()
      
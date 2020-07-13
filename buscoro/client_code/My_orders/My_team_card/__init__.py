from ._anvil_designer import My_team_cardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

from ... import server
from ... import nav_logic

class My_team_card(My_team_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    if self.item['public'] is not None:
      self.label_status_value.text="Status: Equipo en publico"
      # Get initial count down if the team is public.
      self.count_down=server.get_time_count_down(self.item)
      self.total_second_count_down=172800-self.count_down['time_diff']
    else:
      self.label_status_value.text="Status: Equipo pendiente"
      # Get initial count down if the team is private.
      self.count_down=server.get_time_count_down(self.item)
      self.total_second_count_down=86400-self.count_down['time_diff']
    
    self.timer_count_down_tick()
    
  # Display remaining time.
  def timer_count_down_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    with anvil.server.no_loading_indicator:
      self.total_second_count_down-=1
      # Don't allow the clock to go negative.
      if self.total_second_count_down<0:
        self.label_count_down.text="0:0:0"
      else:
        self.label_count_down.text=self.change_time_format(self.total_second_count_down)
        
      self.refresh_data_bindings(self.label_count_down.text)
      
  def change_time_format(self, total_second):
    # total_second = hour*3600 + minute*60 + second = hour*3600 + min_sec
    # min_sec = minute*60 + second
    hour=total_second//3600
    min_sec=total_second%3600
    minute=min_sec//60
    second=min_sec%60
    hour_minute_second="{0}:{1}:{2}".format(hour, minute, second)
    return hour_minute_second
   
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
      
  def link_cancel_team_click(self, **event_args):
    """This method is called when the button is clicked"""
    # Create a copy of the requested cancellation order and serve a confirmation form.
    cancel = alert(
      content="Your team cannot be restored after being canceled and you would need to recreate the team if you want to purchase again. Are you sure that you want to cancel this team?",
      title="Cancelar este equipo", 
      buttons=[("SI, CANCELAR", True), ("AHORA NO", False)]
    )

    # If user confirms to cancel, change the order status and send him/her an email.
    if cancel:
      server.cancel_team(self.item)
      alert("Tu equipo ha sido cancelado.")
      self.card_pending_order.visible=False
      self.refresh_data_bindings(self.card_pending_order.visible)
      
  def link_copy_url_click(self, **event_args):
    """This method is called when the link is clicked"""
    url="https://bazari.anvil.app/#?code=" + self.item['code']
    anvil.js.call_js('copyPageUrl', url)

  def copied_url(self):
    self.link_copy_url.text="Copiado URL!"
    self.link_copy_url.foreground='#666666'
    self.link_copy_url.icon='fa:check'
    self.timer_notify.interval=3
    
  # After 3 seconds, the copy link comes back to normal.
  def timer_notify_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    self.link_copy_url.text="Copiar URL."
    self.link_copy_url.icon='fa:clone'
    self.link_copy_url.foreground='' 
    self.timer_notify.interval=0  


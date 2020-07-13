from ._anvil_designer import Create_teamTemplate
from anvil import *
import anvil.server
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.js

class Create_team(Create_teamTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.

  def link_copy_code_click(self, **event_args):
    """This method is called when the link is clicked"""
    anvil.js.call_js('copyPageUrl', self.item['code'])

  def link_copy_url_click(self, **event_args):
    """This method is called when the link is clicked"""
    url="https://bazari.anvil.app/#?code=" + self.item['code']
    anvil.js.call_js('copyPageUrl', url)
    
  def copied_code(self):
    self.link_copy_code.text="Copiado codigo!"
    self.link_copy_code.foreground='#666666'
    self.link_copy_code.icon='fa:check'
    self.timer_notify.interval=3
    self.tick_from='copied_code'

  def copied_url(self):
    self.link_copy_url.text="Copiado URL!"
    self.link_copy_url.foreground='#666666'
    self.link_copy_url.icon='fa:check'
    self.timer_notify.interval=3
    self.tick_from='copied_url'
    
  # After 3 seconds, the copy link comes back to normal.
  def timer_notify_tick(self, **event_args):
    """This method is called Every [interval] seconds. Does not trigger if [interval] is 0."""
    if self.tick_from is 'copied_code':
      self.link_copy_code.text="Copiar codigo."
      self.link_copy_code.icon='fa:clone'
      self.link_copy_code.foreground=''
    elif self.tick_from is 'copied_url':
      self.link_copy_url.text="Copiar URL."
      self.link_copy_url.icon='fa:clone'
      self.link_copy_url.foreground=''
      
    self.timer_notify.interval=0  

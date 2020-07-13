from ._anvil_designer import Existing_team_cardTemplate
from anvil import *
import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from ... import Purchase_logic
from ... import server

class Existing_team_card(Existing_team_cardTemplate):
  def __init__(self, **properties):
    # Set Form properties and Data Bindings.
    self.init_components(**properties)

    # Any code you write here will run when the form opens.
    self.public_team=self.item
    
    # Get initial count down.
    self.count_down=server.get_time_count_down(self.public_team)
    self.total_second_count_down=172800-self.count_down['time_diff']
    self.timer_count_down_tick()
 
  def button_join_team_click(self, **event_args):
    """This method is called when the button is clicked"""
    print('existing team')
    confirm=Purchase_logic.join_public_team(self.public_team, anvil.users.get_user())
    if confirm:
      self.visible=False

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


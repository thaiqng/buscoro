import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from . import nav_logic
from . import Purchase_logic
from . import server

nav_logic.go_to_home()

# URL hash with the form https://bazari.anvil.app/#?code=[code]. 
url_hash=anvil.get_url_hash()
if url_hash:
  Purchase_logic.join_private_team(anvil.users.get_user(), url_hash['code'])
  
# Run team scraping as a background task to check if any team should be made public or expired.
with anvil.server.no_loading_indicator:
  server.launch_auto_search_and_update_team()
  
# Error handling function. The error message has the form "AnvilWrappedError: [message] on line [number]"
def error_handler(error_message):
  error_string=str(error_message)
  strip_end_message=error_string[:error_string.index(" on line")]
  strip_both_message=strip_end_message.replace("AnvilWrappedError: ", "")  
  anvil.Notification(strip_both_message, timeout=3).show()

anvil.set_default_error_handling(error_handler)

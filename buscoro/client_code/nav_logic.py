import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

# This module contains the navigation logic.

# There are 05 top-level forms (hereby called 'form'): Home, Product_info, Brand_page, My_profile, and My_orders.
#
# Home calls 06 child-level forms (hereby called 'content'): Explore_brands (including Brand_card), Explore_products (including Product_card_single, Product_card_double), and My_account.
# Product_info calls 02 contents: Existing_team_card and Product_picture_card.
# Brand_page calls 0 unique content (01 content in total): (Product_card_double).
# My_profile calls 0 content.
# My_orders calls 02 content: My_order_card and My_team_card.
#
# There are 11 pop-up forms: Cancel_order_confirmation, Cancel_team_confirmation, Edit_address_inquiry, Edit_info_inquiry, Reset_password_confirmation, Sign_out_confirmation, Buy_single_confirmation, Buy_team_confirmation, New_team_information, Join_team_inquiry, Join_team_confirmation.

# Initialize initial form, content, and category. Form, content, and current_category are set in the client-facing logic.
form=None
content=None
content_name=None
current_category='hot'

# This part creates variables to supports the go-back function.
# Initialize global variables storing the 'previous page', brand/product identifier, previous category, and temporary page.
# nav_logic.origin is exclusively used in the back buttons to navigate back to the previous page.
# Global search (Ctrl+Shift+F) "nav_logic.origin" to trace back button flow.
origin='Explore_products'
identifier=None
temporary=False

# Back to previous page.
def go_back():
  if temporary=='product':
    go_to_product_info(identifier)
  elif temporary=='brand':
    go_to_brand_page(identifier)
  else:
    if origin=='Explore_products':
      go_to_home()
      load_explore_products()
    elif origin=='Explore_brands':
      go_to_home()
      load_explore_brands()
    elif origin=='My_account':
      go_to_home()
      load_my_account()
    elif origin=='My_orders':
      go_to_my_orders()
      
# Go to Home.
def go_to_home():
  anvil.open_form('Home')
  
# Go to Brand_page.
def go_to_brand_page(brand_code_name):
  anvil.open_form('Brand_page', brand_code_name)

# Go to Product_info.
def go_to_product_info(sku):
  anvil.open_form('Product_info', sku)
  
# Load Explore_products. Default category is 'hot'.
def load_explore_products():
  global content_name
  
  content_name="product"
  form.load_content(content)
  form.category_highlight()
  form.content_highlight()

# Load to Explore_brands. Default category is 'hot'.
def load_explore_brands():
  global content_name
  
  content_name="brand"
  form.load_content(content)
  form.category_highlight()
  form.content_highlight()
  
# Load My_account.
def load_my_account():
  global content_name
  
  content_name="account"
  form.load_content(content)
  form.content_highlight()
  
# Go to My_profile
def go_to_my_profile():
  anvil.open_form('My_profile')

# Go to My_orders.
def go_to_my_orders():
  anvil.open_form('My_orders')

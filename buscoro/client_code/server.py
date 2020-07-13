import anvil.google.auth, anvil.google.drive
from anvil.google.drive import app_files
import anvil.server
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables

from datetime import datetime, timedelta

# This is the data access layer.

# This is to initialize browser caching.
# The list of cached data includes: current user (including the associated pending/completed orders and pending teams), products (including the associated brands and public teams), brands (including the associated products), and all categories.
__user=None
__teams_and_orders={} # because python filter() only works on SearchIterable and a SuspensionError will be thrown if filter() is called on LiveObject list's elements, the function has to be implemented on the server.
__products={} # for efficient data access, the product is stored according to its category {'category_name': 'product', ...}.
__public_teams={} # for performance pending teams aren't included in the Products table. Because only a portion of the collection will be consumed at a time so the public team data is stored in group of product {'product': [product's public teams], ...} for efficient data access.
__brands={} # for efficient data access, the brand is stored according to its category {'category_name': 'brand', ...}.
__categories=[]

# CREATE operations.
# Create pending order.
def create_pending_order(new_order, refresh=True, verify_user_permission=True):
  global __user, __teams_and_orders
  if refresh:
    __user=None
    __teams_and_orders={}
    
  return anvil.server.call('create_pending_order', new_order, verify_user_permission)
    
# Create new team.
def create_team(new_team):
  global __user, __teams_and_orders
  __user=None
  __teams_and_orders={}
  
  return anvil.server.call('create_team', new_team)

# READ operations: operations with server call.
# Get user.
def get_user():
  global __user

  if __user:
    return __user
  
  # If cache is not used, make a server call.
  print("Server call: user")
  if anvil.users.get_user():
    __user=anvil.users.get_user()
  else:
    __user=anvil.users.login_with_form()
  return __user
  
# Get user's teams and orders:
def get_user_teams_and_orders():
  global __teams_and_orders

  if __teams_and_orders:
    return __teams_and_orders
  
  # If cache is not used, make a server call.
  print("Server call: teams_and_orders") 
  __teams_and_orders=anvil.server.call('get_user_teams_and_orders', get_user())
  return __teams_and_orders

# Get team by team code.
def get_team_by_team_code(team_code):
  return anvil.server.call('get_team_by_team_code', team_code)

# Get public team by product. 
def get_all_unrealized_public_teams_by_product(product):
  global __public_teams

  if product in __public_teams.keys():
    return __public_teams[product]
  
  # If cache is not used, make a server call.
  print("Server call: public_teams") 
  __public_teams.update(
    {product: anvil.server.call('get_all_unrealized_public_teams_by_product', product)}
  )
  return __public_teams[product]
  
# Get all products.
def get_all_products():
  global __products, __brands
  
  if __products:
    return __products
  
  # If cache is not used, make a server call.
  print("Server call: products")
  __products=anvil.server.call('get_all_products_category_sorted', get_all_categories())
  return __products  

# Get all brands.
def get_all_brands():
  global __brands, __products

  if __brands:
    return __brands
  
  # If cache is not used, make a server call.
  print("Server call: brands")
  __brands=anvil.server.call('get_all_brands_category_sorted', get_all_categories())
  return __brands  

# Get all categories.
def get_all_categories():
  global __categories
  
  if __categories:
    return __categories
  
  # If cache is not used, make a server call.
  print("Server call: categories")
  __categories=anvil.server.call('get_all_categories')
  return __categories
  
# READ operations: operations without server calls.
# Get all pending orders.
def get_all_pending_orders():
  return get_user_teams_and_orders()['pending_order']

# Get all completed orders.
def get_all_completed_orders():
  return get_user_teams_and_orders()['completed_order']
    
# Get teams by creator.
def get_all_pending_teams_by_creator():
  return get_user_teams_and_orders()['pending_team']

# Get all products with the given category. The function returns None if there is no product in the given category.
def get_all_products_by_category(category_name):
  return get_all_products()[category_name]
  
# Get a single product with a given unique SKU.
def get_product_by_sku(sku, category_name):
  products_by_category=get_all_products_by_category(category_name)
  
  if products_by_category:
    products_by_sku=list(filter(
      lambda product: product['sku'] is sku, products_by_category
    ))
    
    if products_by_sku:
      return products_by_sku[0]

# Get all brands with the given category. The function returns None if there is no brand in the given category.
def get_all_brands_by_category(category_name):
  return get_all_brands()[category_name]
  
# Get a single brand with a given unique code name.
def get_brand_by_code_name(code_name, category_name):
  brands_by_category=get_all_brands_by_category(category_name)
  
  if brands_by_category:
    brands_by_code_name=list(filter(
      lambda brand: brand['code_name'] is code_name, brands_by_category
    ))
    
    if brands_by_code_name:
      return brands_by_code_name[0]

# Get time count down. This is implemented twice, one on the server and one on the client to avoid making server call.
def get_time_count_down(team):
  now=datetime.now(anvil.tz.tzutc())
  time_delta=(now-team['created'])
  
  # time_delta has the form [days, seconds]
  if time_delta.days==2:
    time_diff=time_delta.seconds+172800
  elif time_delta.days==1:
    time_diff=time_delta.seconds+86400
  else:
    time_diff=time_delta.seconds

  count_down={
    'is_24_hours': False,
    'is_48_hours':False,
    'time_diff': time_diff
  }
    
  # 24 hours equal 86400 seconds.
  if time_diff>=86400 and time_diff<172800:
    count_down['is_24_hours']=True
  elif time_diff>=172800:
    count_down['is_48_hours']=True
    
  return count_down

# UPDATE operations.
# Update user.
def update_user(user_copy):
  global __user
  __user=None
  
  anvil.server.call('update_user', anvil.users.get_user(), user_copy)

# Reset user password.
def reset_password(email):
  anvil.server.call('reset_password', email)
  
# Realize team.
def realize_team(team, team_copy):
  global __user, __teams_and_orders, __public_teams
  __user=None
  __teams_and_orders={}
  __public_teams={}
  
  anvil.server.call('realize_team', team, team_copy)

# DELETE operations.
# Sign out user and clear cache.
def sign_out():
  global __user, __teams_and_orders
  __user=None
  __teams_and_orders={}
  
  anvil.server.call('sign_out')
  
# Cancel team.
def cancel_team(team):
  global __user, __teams_and_orders
  __user=None
  __teams_and_orders={}
  
  anvil.server.call('cancel_team', team)
  
# Request order cancellation.
def request_order_cancellation(order):
  global __user, __teams_and_orders
  __user=None
  __teams_and_orders={}
  
  anvil.server.call('request_order_cancellation', order)

# Lauch check team background task.
def launch_auto_search_and_update_team():
  return anvil.server.call('launch_auto_search_and_update_team')
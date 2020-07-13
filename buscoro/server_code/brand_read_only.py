import anvil.secrets
import anvil.google.auth, anvil.google.drive, anvil.google.mail
from anvil.google.drive import app_files
import anvil.email
import anvil.facebook.auth
import anvil.users
import anvil.tables as tables
import anvil.tables.query as q
from anvil.tables import app_tables
import anvil.server

@anvil.server.callable
def get_all_brands_time_sorted():
  return app_tables.brands.search(
    tables.order_by("created", ascending=False)
  )
@anvil.server.callable
def get_all_brands_by_category(category):
  brands_by_category=app_tables.brands.search(category=[category])
  
  if len(brands_by_category) is not 0:
    return brands_by_category

# This return a dictionary of keys and values, with keys are the category name and values are the lists of brands belong to that categories (which might contain duplicated product data).
@anvil.server.callable
def get_all_brands_category_sorted(categories):  
  all_brands_category_sorted={}
  
  for category in categories:
    all_brands_category_sorted.update(
      {category['category_name']: get_all_brands_by_category(category)}
    )
    
  return all_brands_category_sorted
    
@anvil.server.callable
def get_brand_by_code_name(code_name):
  return app_tables.brands.get(code_name=code_name)

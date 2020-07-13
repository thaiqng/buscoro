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
def get_all_products_time_sorted():
  return app_tables.products.search(
    tables.order_by("created", ascending=False)
  )

@anvil.server.callable
def get_all_products_by_category(category):
  products_by_category=app_tables.products.search(category=[category])
  
  if len(products_by_category) is not 0:
    return products_by_category

# This return a dictionary of keys and values, with keys are the category name and values are the lists of products belong to that categories (which might contain duplicated product data).
@anvil.server.callable
def get_all_products_category_sorted(categories):  
  all_products_category_sorted={}
  
  for category in categories:
    all_products_category_sorted.update(
      {category['category_name']: get_all_products_by_category(category)}
    )
    
  return all_products_category_sorted

@anvil.server.callable
def get_product_by_sku(sku):
  return app_tables.products.get(sku=sku)

@anvil.server.callable
def get_all_categories():
  return app_tables.categories.search()

@anvil.server.callable
def get_category(category):
  return app_tables.categories.get(category=category)
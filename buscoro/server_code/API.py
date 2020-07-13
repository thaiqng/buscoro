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
import uuid
import re
from . import pending_order_management
from . import team_management
from . import user_management

# Compare the client JWT to the server JWT.
def check_client(client_jwt):
  if client_jwt == anvil.secrets.get_secret('jwt'):
    return True
  else:
    return False

# Check if user's passed API key is valid given the user's email and return the user and the error. This is NOT an end-point.
def verify_user_session(data):
  # Check if there is data submitted as a JSON body.
  if data:
    email=data.get('email')
    api_key=data.get('api_key')
    
    # Check if email and API key are submitted.
    if email and api_key:
      user=app_tables.users.get(email=email)

      # Check if the user is authorized to sign in. Must catch exception because login_with_email raises Exception instead of None if authentication fails.
      if user:
        
        # Check for API key that will be passed to authorize other HTTP requests.
        if api_key == user['api_key']:
          return user, None
        else:
          return None, anvil.server.HttpResponse(401, "Invalid API key.")
      else:
        return None, anvil.server.HttpResponse(401, "The user with this email does not exist.")
    else:
      return None, anvil.server.HttpResponse(400, "Email and API key are required.")
  else:
    return None, anvil.server.HttpResponse(400, "You must submit a JSON body via POST.")  

# Sign in flow: user inputs email and password, server return the user API key. This is used instead of Anvil built-in require_credentials because we want to use custom client-side sign in form.
@anvil.server.http_endpoint('/new_user_session', methods=['POST', 'DELETE'])
def new_user_session(**param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if param != {}:
    return anvil.server.HttpResponse(400, "This method doesn't expect any query param.") 
  
  data=anvil.server.request.body_json
  
  # Check if there is data submitted as a JSON body.
  if data:
    email=data.get('email')
    password=data.get('password')
    remember_login=data.get('remember') if data.get('remember') else False
    
    # Check if email and password are submitted.
    if email and password:
      
      # Check if the user is authorized to sign in. Must catch exception because login_with_email raises Exception instead of None if authentication fails.
      try:
        user=anvil.users.login_with_email(email, password, remember=remember_login)
        
        # Create new user session.
        if anvil.server.request.method == 'GET':
          # Check for API key that will be passed to authorize other HTTP requests.
          if user['api_key']:
            api_key_mode="Existing API key"
          else:
            user['api_key']=str(uuid.uuid4())
            api_key_mode="New API key"
          
          # Return the user's API key.
          return {
            'email': user['email'],
            'api_key': user['api_key'],
            'mode': api_key_mode
          } 
        
        # Delete the user session's API key.
        elif anvil.server.request.method == 'DELETE':
          # Check for API key that will be passed to authorize other HTTP requests.
          if user['api_key']:
            user_copy=user
            user_copy['api_key']=None
            try:
              new_session=user_management.update_user(user, user_copy)
              anvil.users.logout()
              return {
                'email': new_session['email'],
                'api_key': new_session['api_key'],
              }
            except:
              return anvil.server.HttpResponse(404, "This user does not exist.")
          else:
            return anvil.server.HttpResponse(400, "Session's API key is required.")
      
      except anvil.users.AuthenticationFailed:
        return anvil.server.HttpResponse(401, "Invalid login.")
    else:
      return anvil.server.HttpResponse(400, "Email and password are required.")
  else:
    return anvil.server.HttpResponse(400, "You must submit a JSON body via POST.")

# User methods.
@anvil.server.http_endpoint('/new_user', methods=['POST'])
def new_user(**param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if param != {}:
    return anvil.server.HttpResponse(400, "This method doesn't expect any query param.")

  data=anvil.server.request.body_json
  
  if not data:
    return None, anvil.server.HttpResponse(400, "You must submit a JSON body via POST.")    
    
  email=data.get('email')
  password=data.get('password')
  remember_login=data.get('remember') if data.get('remember') else False
  
  if not email or not password:
    return anvil.server.HttpResponse(400, "Email and password are required.")
  
  if not re.search('^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', email):
    return anvil.server.HttpResponse(400, "Invalid email.")
   
  try:
    user=anvil.users.signup_with_email(email, password, remember=remember_login)
  except anvil.users.UserExists:
    return anvil.server.HttpResponse(400, "User with this email already exists.")    
  except anvil.users.PasswordNotAcceptable:
    return anvil.server.HttpResponse(400, "Unsecure password (secure password must be at least 8 characters long and have not been previously leaked online).")

  return {
    'email': user['email'],
    'created': user['created']
  }

@anvil.server.http_endpoint('/users/:user_id', methods=['GET', 'PUT'])
def users(user_id, **param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if "data" not in param.keys() or param['data'] != "profile_picture" or param['data'] != "user" or param['data'] != "teams_and_orders" or param['data'] != "password":
    return anvil.server.HttpResponse(400, '"data" query with the value of "profile_picture" or "user" or "teams_and_orders" is expected.')

  if user_id != "self":
    return anvil.server.HttpResponse(401, "You can only access your own account.")
  
  data=anvil.server.request.body_json
  user, error=verify_user_session(data)
  
  if error:
    return error
  
  # Get user profile picture.
  if anvil.server.request.method == 'GET' and param['data'] == "profile_picture":
    return {'profile_picture': user['profile_picture']}
    
  # Get user core information.
  elif anvil.server.request.method == 'GET' and param['data'] == "user":   
    return {
      'name': user['name'],
      'email': user['email'],
      'phone': user['phone'],
      'address': user['address'],
      'signed_up': user['signed_up'].isoformat(),
      'updated': user['updated'].isoformat() if user['updated'] else None,
      'remembered_logins': user['remembered_logins'],
      'last_login': user['last_login'].isoformat() if user['updated'] else None,
    }
  
  # Get user pending teams and pending orders.
  elif anvil.server.request.method == 'GET' and param['data'] == "teams_and_orders":
    if user['pending_team'] is None:
      user['pending_team']=[]
    if user['pending_order'] is None:
      user['pending_order']=[]
      
    pending_teams=list(filter(
      lambda team: team['defunct'] is None, user['pending_team']
    ))
    pending_orders=list(filter(
      lambda order: order['completed'] is None, user['pending_order']
    ))
    completed_orders=list(filter(
      lambda order: order['completed'] is not None, user['pending_order']
    ))

    return {
      'pending_order': [
        {
          'order_id': user_pending_order['order_id'],
          'user': user_pending_order['user']['email'],
          'product': user_pending_order['product']['sku'],
          'team_purchase': user_pending_order['team_purchase']['code'] if user_pending_order['team_purchase'] else None,
          'status': user_pending_order['status']['status'],
          'created': user_pending_order['created'].isoformat(),
          'completed': None,
          'cancellation_requested': user_pending_order['cancellation_requested'].isoformat() if user_pending_order['cancellation_requested'] else None,
          'canceled': user_pending_order['canceled'].isoformat() if user_pending_order['canceled'] else None,
          'returned': None
        } for user_pending_order in pending_orders
      ] if pending_orders else [],
      'completed_order': [
        {
          'order_id': user_pending_order['order_id'],
          'user': user_pending_order['user']['email'],
          'product': user_pending_order['product']['sku'],
          'team_purchase': user_pending_order['team_purchase']['code'] if user_pending_order['team_purchase'] else None,
          'status': user_pending_order['status']['status'],
          'created': user_pending_order['created'].isoformat(),
          'completed': user_pending_order['completed'].isoformat(),
          'cancellation_requested': user_pending_order['cancellation_requested'].isoformat() if user_pending_order['cancellation_requested'] else None,
          'canceled': None,
          'returned': user_pending_order['returned'].isoformat() if user_pending_order['returned'] else None
        } for user_completed_order in completed_orders
      ] if completed_orders else [],
      'pending_team': [
        {
          'creator': user_pending_team['creator'],
          'member': None,
          'product': user_pending_team['product']['sku'],
          'code': user_pending_team['code'],
          'created': user_pending_team['created'].isoformat(),
          'public': user_pending_team['public'].isoformat() if user_pending_team['public'] else None,
          'realized': None,
          'canceled': None,
          'defunct': None,
          'status': user_pending_team['status']['status']
        } for user_pending_team in pending_teams
      ] if pending_teams else []
    }

  # Update user information.
  elif anvil.server.request.method == 'PUT' and param['data'] == "user":
    user_copy=user  
    name=data.get('name')
    phone=data.get('phone')
    address=data.get('address')
  
    if not name and not phone and not address:
      return anvil.server.HttpResponse(400, "At least one of name, phone, and address is required.")
  
    if name:
      if not name.isalnum():
        return anvil.server.HttpResponse(400, "Invalid name (must contain only alphanumeric characters).")    
      user_copy['name']=name
    
    if phone:
      if not phone.isdigit() or len(phone) > 12 or len(phone) < 8:
        return anvil.server.HttpResponse(400, "Invalid phone number (must be int type, contain only numbers, and have 8 to 12 digits ).")
      user_copy['phone']=int(phone)
      
    if address:
      if "street" not in address.keys() or "colony" not in address.keys() or "city" not in address.keys() or "state" not in address.keys() or "zip" not in address.keys():
        return anvil.server.HttpResponse(400, "Missing address information.")
      user_copy['address']=address
        
    try:
      updated_user=user_management.update_user(user, user_copy)
      return {
        'email': updated_user['email'],
        'upadated': updated_user['updated']
      }
    except:
      return anvil.server.HttpResponse(404, "This user does not exist.")

  # Update user password.
  elif anvil.server.request.method == 'PUT' and param['data'] == "password":
    anvil.users.send_password_reset_email(user['email'])
    return {
      'email': user['email'],
      'requested': datetime.now()
    }
        
# Team methods.
@anvil.server.http_endpoint('/new_team', methods=['POST'])
def new_team(**param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if param != {}:
    return anvil.server.HttpResponse(400, "This method doesn't expect any query param.")
  
  data=anvil.server.request.body_json
  user, error=verify_user_session(data)
  
  if error:
    return error
  
  product=app_tables.products.get(sku=data.get('sku'))
  
  if product is None:
    return anvil.server.HttpResponse(404, "Cannot find a product with the given SKU.")
  
  new_team={
    'creator': user,
    'product': product
  }
  
  try:
    created_team=team_management.create_team(new_team)
  except:
    return anvil.server.HttpResponse(401, "You don't have the permission to create this team.")

  return {
    'code': created_team['code'],
    'product': created_team['product']['name'],
    'price': created_team['product']['price_team'],
    'created': created_team['created'],
    'status': created_team['status']['status']
  }

@anvil.server.http_endpoint('/teams/:team_id', methods=['GET', 'PUT', 'DELETE'])
def teams(team_id, **param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if anvil.server.request.method == 'GET':
    if "data" not in param.keys() or param['data'] != "team_by_id" or param['data'] != "public_teams_by_product":
      return anvil.server.HttpResponse(400, '"data" query with the value of "team_by_id" or "public_teams_by_product" is expected.')
 
    # Get team by team code.
    if param['data'] == "team_by_id":
      team=app_tables.pending_teams.get(code=team_id)
    
      if team:
        return {
          'creator': team['creator']['email'],
          'member': team['member']['email'] if team['member'] else None,
          'product': team['product']['sku'],
          'code': team['code'],
          'created': team['created'].isoformat(),
          'public': team['public'].isoformat() if team['public'] else None,
          'realized': team['realized'].isoformat() if team['realized'] else None,
          'canceled': team['canceled'].isoformat() if team['canceled'] else None,
          'defunct': team['defunct'].isoformat() if team['defunct'] else None,
          'status': team['status']['status']
        }
      else:
        return anvil.server.HttpResponse(404, "Cannot find a team with the given team code.")
    
    # Get public teams by product.
    elif param['data'] == "public_teams_by_product":
      if team_id.isdigit():
        sku=int(team_id)
      else:
        return anvil.server.HttpResponse(400, "SKU must be an integer.")     
      
      product=app_tables.products.get(sku=sku)
      
      if product:  
        return [
          {
            'creator': team['creator']['email'],
            'member': None,
            'product': team['product']['sku'],
            'code': team['code'],
            'created': team['created'].isoformat(),
            'public': team['public'].isoformat(),
            'realized': None,
            'canceled': None,
            'defunct': None,
            'status': team['status']['status']        
          }
          for team in app_tables.pending_teams.search(
            public=q.none_of(None),
            product=product,
            realized=None,
            canceled=None,
            defunct=None
          )
        ]
      else:
        return anvil.server.HttpResponse(404, "Cannot find a product with the given SKU.")
    
  # Realize team.
  elif anvil.server.request.method == 'PUT':
    if param != {}:
      return anvil.server.HttpResponse(400, "This method doesn't expect any query param.")
    
    data=anvil.server.request.body_json
    user, error=verify_user_session(data)
    
    if error:
      return error
  
    team=app_tables.pending_teams.get(code=team_id)
    team_copy=team
    team_copy['member']=user
    
    try:
      updated_team=team_management.realize_team(team, team_copy)
      return {
        'code': updated_team['code'],
        'product': updated_team['product']['name'],
        'price': updated_team['product']['price_team'],
        'realized': updated_team['realized'],
        'status': updated_team['status']['status']
      }
    except:
      anvil.server.HttpResponse(404, "This team is no longer available.")
      
  # Request team cancellation.
  elif anvil.server.request.method == 'DELETE':
    if param != {}:
      return anvil.server.HttpResponse(400, "This method doesn't expect any query param.")
    
    data=anvil.server.request.body_json
    user, error=verify_user_session(data)
    
    if error:
      return error
    
    if not user['pending_team']:
      return anvil.server.HttpResponse(404, "The user has no team.")
      
    team=list(filter(
      lambda team: team['defunct'] is None and team['code'] == team_id, user['pending_team']
    ))
    
    if not team:
      return anvil.server.HttpResponse(404, "The user does not have a team with this team code.")
    
    try:
      team_management.cancel_team(team)
    except:
      anvil.server.HttpResponse(404, "This team is no longer available.")
      
    return {
      'code': team['code'],
      'canceled': team['canceled']
    }

# Product methods.
__product_pictures=None
@anvil.server.http_endpoint('/products/product_id', methods=['GET'])
def products(product_id, **param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if "data" not in param.keys() or param['data'] != "product" or param['data'] != "picture":
    return anvil.server.HttpResponse(400, '"data" query with the value of "product" or "picture" is expected.')
  
  # Get product information.
  if param['data'] == "product":
    if product_id != "all": 
      return anvil.server.HttpResponse(400, "You can only request all products by passing /all.")
      
    return [
      {
        'sku': product['sku'],
        'name': product['name'],
        'description': product['description'],
        'price_single': product['price_single'],
        'price_team': product['price_team'],
        'created': product['created'].isoformat(),
        'thumbnail': str(product['thumbnail']['order']-1),
        'picture': str(len(product['picture'])),
        'category': [{'category_name': product_category['category_name']} for product_category in product['category']],
        'brand': {'code_name': product['brand']['code_name']}
      }
      for product in app_tables.products.search()
    ]
  
  # Get product pictures and thumbnail.
  elif param['data'] == "picture":
    global __product_pictures
  
    if product_id.isdigit():
      sku=int(product_id)
    else:
      return anvil.server.HttpResponse(400, "SKU must be an integer.")    
    
    if app_tables.products.get(sku=sku):
      if "id" in param.keys() and param['id'].isdigit():
        index=int(param['id'])
        
        # If the product pictures aren't stored locally or it's not the right product, get the product pictures.
        if __product_pictures is None or sku is not __product_pictures[0]['product']['sku']:
          __product_pictures=app_tables.product_pictures.search(
            tables.order_by('order'),
            product=app_tables.products.get(sku=sku)
          )
        
        # Check if out of range.
        if index < len(__product_pictures):
          return __product_pictures[index]['picture']
        else:
          return anvil.server.HttpResponse(400, "Index is out of range.")        
      else:
        return anvil.server.HttpResponse(400, "Invalid data request.")
    else:
      return anvil.server.HttpResponse(404, "Cannot find a product with the given SKU.")
 
# Get brand methods.
@anvil.server.http_endpoint('/brands/:brand_id', methods=['GET'])
def brands(brand_id, **param): 
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if "data" not in param.keys() or param['data'] != "brand" or param['data'] != "logo" or param['data'] != "banner":
    return anvil.server.HttpResponse(400, '"data" query with the value of "brand" or "logo" or "picture" is expected.')
  
  # Get brand information.
  if param['data'] == "brand":
    if brand_id != "all": 
      return anvil.server.HttpResponse(400, "You can only request all brands by passing /all.")
    
    return [
      {
        'name': brand['name'],
        'code_name': brand['code_name'],
        'description': brand['description'],
        'created': brand['created'].isoformat(),
        'category': [{'category_name': brand_category['category_name']} for brand_category in brand['category']],
        'product': [{'sku': brand_product['sku']} for brand_product in brand['product']]
      }
      for brand in app_tables.brands.search()
    ]
  
  # Get brand logo.
  elif param['data'] == "logo":
    if not app_tables.brands.get(code_name=code_name):
      return anvil.server.HttpResponse(404, "Cannot find a brand with the given code name.")
      
    return app_tables.brands.get(code_name=code_name)['logo']
  
  # Get brand banner.
  elif param['data'] == "banner":
    if not app_tables.brands.get(code_name=code_name):
      return anvil.server.HttpResponse(404, "Cannot find a brand with the given code name.")
    
    return app_tables.brands.get(code_name=code_name)['banner']
  
# Category methods.
@anvil.server.http_endpoint('/categories', methods=['GET'])
def categories(**param):  
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if param != {}:
    return anvil.server.HttpResponse(400, "This method doesn't expect any query param.")
  
  return [
    {
      'category_name': category['category_name'],
      'spanish_name': category['spanish_name']
    }
    for category in app_tables.categories.search()
  ]

# Order methods.
@anvil.server.http_endpoint('/new_order', methods=['POST'])
def new_order(**param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if "verify_user_permission" not in param.keys() or param['verify_user_permission'] != True or param['verify_user_permission'] != False:
    return anvil.server.HttpResponse(400, '"verify_user_permission" query with the value of True or False is expected.')

  if "team_purchase" not in param.keys() or param['team_purchase'] != True or param['team_purchase'] != False:
    return anvil.server.HttpResponse(400, '"team_purchase" query with the value of True or False is expected.')

  data=anvil.server.request.body_json
  user, error=verify_user_session(data)
  
  if error:
    return error
  
  product=app_tables.products.get(sku=data.get('sku'))
  team_purchase=app_tables.pending_teams.get(code=data.get('code')) if data.get('code') else None
  
  if product is None:
    return anvil.server.HttpResponse(404, "Cannot find a product with the given SKU.")

  try:
    new_order={
      'user': user,
      'product': product,
      'team_purchase': team_purchase
    }
    created_order=pending_order_management.create_pending_order(new_order, verify_user_session=param['verify_user_permission'])
  except:
    return anvil.server.HttpResponse(401, "You don't have the permission to create this order.")

  return {
    'order_id': created_order['order_id'],
    'product': created_order['product']['name'],
    'price': created_order['product']['price_team'] if param['team_purchase'] else created_order['product']['price_single'],
    'created': created_order['created'], 
    'status': created_order['status']['status']
  }

@anvil.server.http_endpoint('/orders/:order_id', methods=['DELETE'])
def orders(order_id, **param):
  client_jwt=anvil.server.request.headers['Authorization']
  if not client_jwt:
    return anvil.server.HttpResponse(400, "You must submit a Authorization header with an appropriate value.")
  if not check_client(client_jwt):
    return anvil.server.HttpResponse(403, "You are not authorized to access this end-point.")
   
  if param != {}:
    return anvil.server.HttpResponse(400, "This method doesn't expect any query param.")
  
  data=anvil.server.request.body_json
  user, error=verify_user_session(data)
  
  if error:
    return error
  
  if not user['pending_order']:
    return anvil.server.HttpResponse(404, "The user has no order.")
    
  order=list(filter(
    lambda order: order['order_id'] == order_id, user['pending_order']
  ))
  
  if not order:
    return anvil.server.HttpResponse(404, "The user does not have an order with this order ID.")
  
  pending_order_management.request_order_cancellation(order)
  return {
    'order_id': order['order_id'],
    'cancellation_requested': order['cancellation_requested']
  }

# Lauch check team background task.
def launch_auto_search_and_update_team():
  return anvil.server.call('launch_auto_search_and_update_team')
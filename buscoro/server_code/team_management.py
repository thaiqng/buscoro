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

from datetime import datetime, timedelta, timezone
from . import user_management
import random
from . import user_management
from . import server

@anvil.server.callable
def create_team(new_team):
  user_management.verify_user_permission(new_team['creator'])
  
  team=app_tables.pending_teams.add_row(
    created=datetime.now(timezone.utc),
    member=None,
    code=create_team_code(new_team['creator']['name']),
    public=None,
    realized=None,
    canceled=None,
    defunct=None,
    status=app_tables.pending_team_statuses.get(status='Active & Private'),
    **new_team
  )
  
  user_copy=dict(list(new_team['creator']))
  if user_copy['pending_team']:
    user_copy['pending_team'].append(team)
  else:
    user_copy['pending_team']=[team]
  user_management.update_user(new_team['creator'], user_copy)
  
  return team

def create_team_code(user_name):
  team_id=hex(random.getrandbits(32))
  formatted_name=user_name.lower().replace(" ", "")
  team_code=formatted_name+"-"+team_id

  return team_code
  
@anvil.server.callable
def get_team_by_team_code(team_code):
  team=app_tables.pending_teams.get(code=team_code)

  # If the team is defunct, pass the status to the front-end.
  if team:
    return team
  
# This method gives all pending teams (not defunct) of a particular user.
@anvil.server.callable
def get_all_pending_teams_by_creator(creator):
  user_management.verify_user_permission(creator)

  teams=app_tables.pending_teams.search(
    tables.order_by("created", ascending=False),
    creator=creator,
    defunct=None
  )
  if len(teams) is not 0:
    return teams

@anvil.server.callable
def realize_team(team, team_copy):
  user_management.verify_user_permission(team_copy['member'])
  
  if team['defunct'] is None:
    team_copy['realized']=datetime.now(timezone.utc)
    team_copy['defunct']=team_copy['realized']
    team_copy['status']=app_tables.pending_team_statuses.get(status='Defunct: realized')
    team.update(**team_copy)
  else:
    raise Exception("This team is no longer available.")
    
@anvil.server.callable
def cancel_team(team):
  user_management.verify_user_permission(team['creator'])
  
  if team['defunct'] is None:
    team_copy=dict(list(team))
    team_copy['canceled']=datetime.now(timezone.utc)
    team_copy['defunct']=team_copy['canceled']
    team_copy['status']=app_tables.pending_team_statuses.get(status='Defunct: canceled')
    team.update(**team_copy)
  else:
    raise Exception("This team is no longer available.")
  
@anvil.server.callable
def get_all_unrealized_public_teams_by_product(product):
  teams=app_tables.pending_teams.search(
    public=q.none_of(None),
    product=product,
    realized=None,
    canceled=None,
    defunct=None
  )

  if len(teams) is not 0:
    return list(teams)

def get_time_count_down(team):
  now=datetime.now(timezone.utc)
  time_delta=(now-team['created'])
  
  # time_delta has the form [days, seconds].
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
    
@anvil.server.background_task
def auto_search_and_update_team():
  number_of_teams_made_public=0
  number_of_teams_made_expired=0
  number_of_team_crawled=0
  
  # Exclude team that is already defunct whether because of being canceled, expired, or realized.
  for team in app_tables.pending_teams.search(defunct=None):
    number_of_team_crawled+=1
    elapsed_time=get_time_count_down(team)
    # If the team has passed the 24-hour mark but not yet pass the 48-hour mark, automatically make the team public.
    if elapsed_time['is_24_hours'] and team['public'] is None:
      team['public']=datetime.now(timezone.utc)
      team['status']=app_tables.pending_team_statuses.get(status='Active & Public')
      number_of_teams_made_public+=1
      
    # If the team has passed the 48-hour mark, the team is expired.
    elif elapsed_time['is_48_hours']:
      team['defunct']=datetime.now(timezone.utc)
      team['status']=app_tables.pending_team_statuses.get(status='Defunct: expired')
      number_of_teams_made_expired+=1
  
  # Print summary to the background tasks log (not the app log).
  print('Total number of team(s) crawled: '+str(number_of_team_crawled))
  print('Team(s) made public: '+str(number_of_teams_made_public))
  print('Team(s) made expired: '+str(number_of_teams_made_expired))
              
@anvil.server.callable
def launch_auto_search_and_update_team():
  task=anvil.server.launch_background_task('auto_search_and_update_team')
  
  # Store the ID of the task so we can see it later.
  app_tables.background_tasks.add_row(
    created=datetime.now(timezone.utc),
    task_id=task.get_id(),
  )
  return task
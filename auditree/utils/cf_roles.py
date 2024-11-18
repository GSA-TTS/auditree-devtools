from subprocess import check_output
import json
from compliance.config import get_config
from cloudfoundry_client.client import CloudFoundryClient

client = CloudFoundryClient.build_from_cf_config()

def retrieve_cf_client(space_name=None):
  if space_name is None:
    guid = check_output(f"cf org {get_config().get('gov.cloud.org-name')} --guid", shell=True).decode().strip()
  else:
    guid = check_output(f"cf space {space_name} --guid", shell=True).decode().strip()
  return (client, guid)


class RoleCollector:
  def __init__(self):
    self._map = {}

  def add(self, role):
    user = role.user
    if self._map.get(user.guid) is None:
      self._map[user.guid] = {"user": user, "roles": [role]}
    else:
      self._map[user.guid]["roles"].append(role)

  def to_json(self):
    data = []
    for user_roles in self._map.values():
      user = user_roles["user"]
      roles = user_roles["roles"]
      data.append({
        "user_guid": user.guid,
        "user_type": user.type,
        "user_name": user.username,
        "roles": list((role.description for role in roles))
      })
    return json.dumps(data)


class User:
  def __init__(self, entity):
    self.guid = entity["guid"]
    self._username = entity["username"]
    self._is_service_account = entity["origin"] != "gsa.gov"
    self.type = "Bot" if self._is_service_account else "User"

  @property
  def username(self):
    if self._is_service_account:
      service_name = client.v3.service_credential_bindings.get(
        self._username, include="service_instance"
      ).service_instance()["name"]
      return f"{service_name} ({self._username})"
    else:
      return self._username


class Space:
  def __init__(self, entity):
    self.name = entity["name"]


class Role:
  def __init__(self, entity):
    self._fields = entity
    self.type = entity["type"]
    self.user = User(entity.user())

  @property
  def description(self):
    if self.space:
      return f"{self.type} in space \"{self.space.name}\""
    else:
      return self.type

  @property
  def space(self):
    try:
      return Space(self._fields.space())
    except AttributeError:
      return None

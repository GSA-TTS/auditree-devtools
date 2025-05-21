import json

from compliance.check import ComplianceCheck
from compliance.evidence import with_raw_evidences, evidences

from compliance.config import get_config

from parameterized import parameterized

from utils.cf import collect_space_names

class SpaceSSHDisabledCheck(ComplianceCheck):
  @property
  def title(self):
    return "Cloud.gov Space SSH Disabled Check"

  @parameterized.expand(get_config().get("gov.cloud.space-names"), skip_on_empty=True)
  def test_space_ssh_disabled(self, space):
    if space == "*":
      for space in collect_space_names():
        self._test_space_ssh_disabled(space)
    else:
      self._test_space_ssh_disabled(space)

  def _test_space_ssh_disabled(self, space):
    evidence_path = f"raw/cf/space-{space}-ssh.json"
    with evidences(self, evidence_path) as evidence:
      evidence = json.loads(evidence.content)
      if evidence["ssh-enabled"] == True:
        self.add_failures("Cloud.gov SSH Access Violation", {"org": evidence['org'], "space": space})
      else:
        self.add_successes("Cloud.gov SSH Access", f"Space {evidence['space']} has disabled SSH access")

  def get_reports(self):
    return ["cf/space-ssh.md"]

class UserRoleReport(ComplianceCheck):
  # failures are covered by empty evidence / abandoned evidence, so this is just gathering the raw evidence into a format
  # useful for a human-readable report

  @property
  def title(self):
    return "User Role Report"

  @property
  def users(self):
    return self._user_map()

  @classmethod
  def _user_map(cls):
    if not hasattr(cls, '_users'):
      cls._users = {}
    return cls._users

  @classmethod
  def _guid_exists(cls, guid):
    return guid in cls._user_map()


  @classmethod
  def _add_user(cls, guid, user):
    cls._user_map()[guid] = {"user_name": user["user_name"], "roles": user["roles"]}


  @classmethod
  def _append_user_roles(cls, guid, user):
    cls._user_map()[guid]["roles"] += user["roles"]


  @with_raw_evidences("raw/cf/org-roles.json")
  def test_org_roles_report(self, evidence):
    self._process_users(evidence)


  @parameterized.expand(get_config().get("gov.cloud.space-names"), skip_on_empty=True)
  def test_user_role_report(self, space):
    if space == "*":
      for space in collect_space_names():
        self._test_user_role_report(space)
    else:
      self._test_user_role_report(space)

  def _test_user_role_report(self, space):
    evidence_path = f"raw/cf/space-{space}-user-roles.json"
    with evidences(self, evidence_path) as evidence:
      self._process_users(evidence)


  def _process_users(self, evidence):
    contents = json.loads(evidence.content)
    for bot in (u for u in contents if u["user_type"] == "Bot"):
      guid = bot["user_guid"]
      if self._guid_exists(guid):
        self._append_user_roles(guid, bot)
      else:
        self._add_user(guid, bot)
        self.add_successes("Service Accounts", guid)

    for user in (u for u in contents if u["user_type"] != "Bot"):
      guid = user["user_guid"]
      if self._guid_exists(guid):
        self._append_user_roles(guid, user)
      else:
        self._add_user(guid, user)
        self.add_successes("Users", guid)


  def get_reports(self):
    return ["cf/user-roles.md"]

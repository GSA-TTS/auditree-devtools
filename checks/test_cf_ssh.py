import json

from compliance.check import ComplianceCheck
from compliance.evidence import with_raw_evidences, evidences

from compliance.config import get_config

from parameterized import parameterized

class SpaceSSHDisabledCheck(ComplianceCheck):
  @property
  def title(self):
    return "Cloud.gov Space SSH Disabled Check"

  @with_raw_evidences("cf/space-ssh.json")
  def test_space_ssh_disabled(self, evidence):
    evidence = json.loads(evidence.content)
    if evidence["ssh-enabled"] == True:
      self.add_failures("Cloud.gov SSH Access Violation", {"org": evidence['org'], "space": evidence['space']})

  def get_reports(self):
    return ["cf/space-ssh.md"]

class AppSSHDisabledCheck(ComplianceCheck):
  @property
  def title(self):
    return "Cloud.gov App SSH Disabled Check"

  @parameterized.expand(get_config().get("gov.cloud.apps"))
  def test_app_ssh_disabled(self, app):
    evidence_path = f"raw/cf/app-ssh-{app}.json"
    with evidences(self, evidence_path) as evidence:
      enabled = json.loads(evidence.content)["ssh-enabled"]
      if enabled == True:
        self.add_failures("Cloud.gov SSH Access Violation", {"app": app})

  def get_reports(self):
    return ["cf/app-ssh.md"]

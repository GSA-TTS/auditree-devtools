import json

from compliance.check import ComplianceCheck
from compliance.evidence import with_raw_evidences

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
      self.add_failures("Cloud.gov SSH Access Violation", f"SSH is enabled for production space: {evidence['space']}")

class AppSSHDisabledCheck(ComplianceCheck):
  @property
  def title(self):
    return "Cloud.gov App SSH Disabled Check"

  @parameterized.expand(get_config().get("org.cloudgov.apps"))
  def test_app_ssh_disabled(self, app):
    evidence = self.locker.get_evidence(f"raw/cf/app-ssh-{app}.json")
    enabled = json.loads(evidence.content)["ssh-enabled"]
    if enabled == True:
      self.add_failures("Cloud.gov SSH Access Violation", f"SSH is enabled for app: {app}")

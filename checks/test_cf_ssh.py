import json

from compliance.check import ComplianceCheck
from compliance.evidence import with_raw_evidences, evidences

from compliance.config import get_config

from parameterized import parameterized

class SpaceSSHDisabledCheck(ComplianceCheck):
  @property
  def title(self):
    return "Cloud.gov Space SSH Disabled Check"

  @parameterized.expand(get_config().get("gov.cloud.space-names"), skip_on_empty=True)
  def test_space_ssh_disabled(self, space):
    evidence_path = f"raw/cf/space-{space}-ssh.json"
    with evidences(self, evidence_path) as evidence:
      evidence = json.loads(evidence.content)
      if evidence["ssh-enabled"] == True:
        self.add_failures("Cloud.gov SSH Access Violation", {"org": evidence['org'], "space": space})
      else:
        self.add_successes("Cloud.gov SSH Access", f"Space {evidence['space']} has disabled SSH access")

  def get_reports(self):
    return ["cf/space-ssh.md"]

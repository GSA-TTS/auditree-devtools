import json
import subprocess

from compliance.evidence import raw_evidence
from compliance.fetch import ComplianceFetcher

from compliance.config import get_config

from parameterized import parameterized

class FetchCfMetadata(ComplianceFetcher):
  @parameterized.expand(get_config().get("gov.cloud.space-names"), skip_on_empty=True)
  def fetch_prod_ssh(self, space):
    evidence_path = f"cf/space-{space}-ssh.json"
    with raw_evidence(self.locker, evidence_path) as evidence:
      if evidence:
        try:
          org = get_config().get("gov.cloud.org-name")
          subprocess.run(["cf", "target", "-o", org], check=True)
          data = {"ssh-enabled": self._get_space_ssh_enabled(space), "org": org, "space": space}
          evidence.set_content(json.dumps(data))
        except:
          evidence.set_content("{}")

  def _get_space_ssh_enabled(self, space_name):
    return not self._get_ssh_disabled("space-ssh-allowed", space_name)

  def _get_ssh_disabled(self, *args):
    result = subprocess.run(["cf", *args], capture_output=True, text=True, check=True).stdout
    if result.startswith("ssh support"):
      return result.startswith("ssh support is disabled")
    else:
      raise AssertionError("stdout did not match expected format")

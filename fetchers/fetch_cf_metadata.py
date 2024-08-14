import json
import subprocess

from compliance.evidence import DAY, RawEvidence, store_raw_evidence, raw_evidence
from compliance.fetch import ComplianceFetcher

from compliance.config import get_config

from parameterized import parameterized

class FetchCfMetadata(ComplianceFetcher):
  @store_raw_evidence("cf/space-ssh.json")
  def fetch_prod_ssh(self):
    config = get_config()
    try:
      data = {"ssh-enabled": self._get_space_ssh_enabled(config.get("gov.cloud.space-name")),
              "org": config.get("gov.cloud.org-name"),
              "space": config.get("gov.cloud.space-name")}
      return json.dumps(data)
    except:
      return "{}"

  @parameterized.expand(get_config().get("gov.cloud.apps"))
  def fetch_app_ssh(self, app):
    evidence_path = f"cf/app-ssh-{app}.json"
    with raw_evidence(self.locker, evidence_path) as evidence:
      if evidence:
        try:
          data = {"ssh-enabled": self._get_app_ssh_enabled(app)}
          evidence.set_content(json.dumps(data))
        except:
          evidence.set_content("{}")

  def _get_space_ssh_enabled(self, space_name):
    return not self._get_ssh_disabled("space-ssh-allowed", space_name)

  def _get_app_ssh_enabled(self, app_name):
    return not self._get_ssh_disabled("ssh-enabled", app_name)

  def _get_ssh_disabled(self, *args):
    result = subprocess.run(["cf", *args], capture_output=True, text=True, check=True).stdout
    if result.startswith("ssh support"):
      return result.startswith("ssh support is disabled")
    else:
      raise AssertionError("stdout did not match expected format")

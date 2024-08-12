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
    data = {"ssh-enabled": self._get_space_ssh_enabled(config),
            "org": config.get("org.cloudgov.org-name"),
            "space": config.get("org.cloudgov.space-name")}
    return json.dumps(data)

  @parameterized.expand(get_config().get("org.cloudgov.apps"))
  def fetch_app_ssh(self, app):
    evidence_path = f"cf/app-ssh-{app}.json"
    with raw_evidence(self.locker, evidence_path) as evidence:
      if evidence:
        data = {"ssh-enabled": self._get_app_ssh_enabled(app)}
        evidence.set_content(json.dumps(data))

  def _get_space_ssh_enabled(self, config):
    result = subprocess.run(["cf", "space-ssh-allowed", config.get("org.cloudgov.space-name")], capture_output=True, text=True).stdout
    return result.startswith("ssh support is enabled")

  def _get_app_ssh_enabled(self, app_name):
    result = subprocess.run(["cf", "ssh-enabled", app_name], capture_output=True, text=True).stdout
    return result.startswith("ssh support is enabled")

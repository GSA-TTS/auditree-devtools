import json
import subprocess

from compliance.evidence import raw_evidence
from compliance.fetch import ComplianceFetcher

from compliance.config import get_config

from parameterized import parameterized

from utils.cf_roles import Role, RoleCollector, retrieve_cf_client

class FetchCfMetadata(ComplianceFetcher):
  def fetch_org_roles(self):
    with raw_evidence(self.locker, "cf/org-roles.json") as evidence:
      if evidence:
        client, org_guid = retrieve_cf_client()
        role_collector = RoleCollector()
        for role in map(Role, client.v3.roles.list(organization_guids=org_guid, include="user")):
          role_collector.add(role)
        evidence.set_content(role_collector.to_json())


  @parameterized.expand(get_config().get("gov.cloud.space-names"), skip_on_empty=True)
  def fetch_space_roles(self, space):
    evidence_path = f"cf/space-{space}-user-roles.json"
    with raw_evidence(self.locker, evidence_path) as evidence:
      if evidence:
        client, space_guid = retrieve_cf_client(space)
        role_collector = RoleCollector()
        for role in map(Role, client.v3.roles.list(space_guids=space_guid, include="user")):
          role_collector.add(role)
        evidence.set_content(role_collector.to_json())

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

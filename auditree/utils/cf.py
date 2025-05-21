from compliance.config import get_config
from cloudfoundry_client.client import CloudFoundryClient

client = CloudFoundryClient.build_from_cf_config()

def org_guid():
  org = get_config().get("gov.cloud.org-name")
  return client.v3.organizations.get_first(names=org)["guid"]

def space_guid(space_name):
  return client.v3.spaces.get_first(names=space_name, organization_guids=org_guid())["guid"]

def collect_space_names():
  return [s["name"] for s in client.v3.spaces.list(organization_guids=org_guid())]

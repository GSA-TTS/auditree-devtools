from arboretum.auditree.fetchers.fetch_abandoned_evidence import AbandonedEvidenceFetcher
from arboretum.auditree.fetchers.fetch_compliance_config import ComplianceConfigFetcher

from compliance.config import get_config
if get_config().get("org.auditree.repo_integrity") is not None:
  from arboretum.auditree.fetchers.github.fetch_repo_metadata import GithubRepoMetaDataFetcher
  from arboretum.auditree.fetchers.github.fetch_branch_protection import GithubRepoBranchProtectionFetcher

import json
from datetime import datetime, timezone
from dateutil.relativedelta import relativedelta

from compliance.check import ComplianceCheck
from compliance.evidence import with_raw_evidences, evidences

from compliance.config import get_config

from parameterized import parameterized

class GovernedReportsCheck(ComplianceCheck):
  @property
  def title(self):
    return "Governed Documents Check"

  def test_governed_documents(self):
    governed_docs = get_config().get("trestle.governed_docs") or []
    for doc_config in governed_docs:
      doc_name = doc_config["name"]
      refresh_interval = doc_config["refresh_interval"]
      evidence_path = f"raw/trestle/{doc_name}.json"
      with evidences(self, evidence_path) as evidence:
        # evidence is list of reports for the given doc name
        last_update = sorted(json.loads(evidence.content), key=lambda x: x["date"], reverse=True)[0]
        last_update_dt = datetime.fromisoformat(last_update["date"])
        match refresh_interval:
          case "annually":
            report_due = last_update_dt + relativedelta(years=1)
          case "monthly":
            report_due = last_update_dt + relativedelta(months=1)
          case "biweekly":
            report_due = last_update_dt + relativedelta(weeks=2)
          case "weekly":
            report_due = last_update_dt + relativedelta(weeks=1)
          case "daily":
            report_due = last_update_dt + relativedelta(days=1)
          case _:
            self.add_warnings(doc_name, f"Unknown refresh_interval `{refresh_interval}`")

        if datetime.now(timezone.utc) > report_due:
          self.add_failures(doc_name, {
            "author": last_update["author"],
            "last_updated": last_update["date"],
            "file_name": last_update["file_name"],
            "interval": refresh_interval
          })

  def get_reports(self):
    return ["trestle/docs.md"]

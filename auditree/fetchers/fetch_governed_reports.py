import json
import os
import frontmatter

from compliance.evidence import raw_evidence
from compliance.fetch import ComplianceFetcher

from compliance.config import get_config

class FetchGoverenedReports(ComplianceFetcher):
  def fetch_reports(self):
    governed_docs = get_config().get("trestle.governed_docs") or []
    for doc_config in governed_docs:
      doc_name = doc_config["name"]
      doc_root = os.path.join(os.getenv("TRESTLE_ROOT", "/app/trestle_root"), doc_name)
      evidence_path = f"trestle/{doc_name}.json"
      results = []
      with raw_evidence(self.locker, evidence_path) as evidence:
        if evidence:
          with os.scandir(doc_root) as docs:
            for doc in docs:
              doc_meta = frontmatter.load(os.path.join(doc_root, doc.name))
              results.append({"file_name": doc.name, "date": doc_meta["date"].isoformat(), "author": doc_meta["author"]})
          evidence.set_content(json.dumps(results))

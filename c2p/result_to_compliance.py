import argparse
from pathlib import Path

import yaml

from c2p.framework.c2p import C2P
from c2p.framework.models import RawResult
from c2p.framework.models.c2p_config import C2PConfig, ComplianceOscal

from auditree_plugin import PluginAuditree

parser = argparse.ArgumentParser()
parser.add_argument(
    '-i',
    '--input',
    type=str,
    help='Path to check_results.json',
    required=True,
)
parser.add_argument(
  '-l',
  '--locker',
  type=str,
  default='https://github.com/gsa-tts/devtools-auditree-evidence',
  help='URL for locker repo. (Default: https://github.com/gsa-tts/devtools-auditree-evidence)',
  required=False,
)
parser.add_argument(
    '-c',
    '--component_definition',
    type=str,
    help='Path to component-definition.json',
    required=True,
)
args = parser.parse_args()

# Setup c2p_config
c2p_config = C2PConfig()
c2p_config.compliance = ComplianceOscal()
c2p_config.compliance.component_definition = args.component_definition
c2p_config.pvp_name = 'Auditree'
c2p_config.result_title = 'Auditree Assessment Results'
c2p_config.result_description = 'OSCAL Assessment Results from Auditree'

# Construct C2P
c2p = C2P(c2p_config)

# Create pvp_result from raw result via plugin
check_results = yaml.safe_load(Path(args.input).open('r'))
pvp_raw_result = RawResult(
    data=check_results,
    additional_props={
        'locker_url': args.locker,
    },
)
pvp_result = PluginAuditree().generate_pvp_result(pvp_raw_result)

# Transform pvp_result to OSCAL Assessment Result
c2p.set_pvp_result(pvp_result)
oscal_assessment_results = c2p.result_to_oscal()

print(oscal_assessment_results.oscal_serialize_json(pretty=True))

import argparse
from pathlib import Path

from c2p.framework.c2p import C2P
from c2p.framework.models.c2p_config import C2PConfig, ComplianceOscal

from auditree_plugin import PluginAuditree, PluginConfigAuditree

parser = argparse.ArgumentParser()
parser.add_argument(
    '-t',
    '--template',
    type=str,
    default='auditree.template.json',
    help=f'Path to auditree.json template (default: auditree.template.json)',
    required=False,
)
parser.add_argument(
    '-c',
    '--component_definition',
    type=str,
    help=f'Path to component-definition.json',
    required=True,
)
parser.add_argument(
    '-o',
    '--out',
    type=str,
    default='auditree.json',
    help='Name of generated auditree.json (default: auditree.json)',
    required=False,
)
args = parser.parse_args()

with Path(args.out).open('w') as output:
    # Setup c2p_config
    c2p_config = C2PConfig()
    c2p_config.compliance = ComplianceOscal()
    c2p_config.compliance.component_definition = args.component_definition
    c2p_config.pvp_name = 'Auditree'
    c2p_config.result_title = 'Auditree Assessment Results'
    c2p_config.result_description = 'OSCAL Assessment Results from Auditree'

    # Construct C2P
    c2p = C2P(c2p_config)

    # Transform OSCAL (Compliance) to Policy
    config = PluginConfigAuditree(auditree_json_template=args.template, output=output.name)
    PluginAuditree(config).generate_pvp_policy(c2p.get_policy())

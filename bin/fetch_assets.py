#!/usr/bin/env python

import argparse
import yaml

from export_qs_analysis_bundle import ExportAnalysisBundle
from export_qs_dashboard_bundle import ExportDashboardBundle

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--deploy_env', type=str,
                        help='QuickSight Deploy Environment')
    parser.add_argument('--local', default=False,
                        help='QuickSight Deploy Local')
    parser.add_argument('--asset_name', default=False,
                        help='QuickSight Asset Name')
    args = parser.parse_args()
    if args.deploy_env is None:
        print('Argument deploy env required.\n')
        exit()
    if args.asset_name is None:
        print('Argument asset name required.\n')
        exit()
    print("deploy env:{}, local:{}, asset name:{}".format(args.deploy_env, args.local, args.asset_name))

    with open("./quicksight.yml", "r") as stream:
        quicksight_config = yaml.load(stream, Loader=yaml.FullLoader)

    export_job_analysis = ExportAnalysisBundle(quicksight_config, args)
    export_job_analysis.export_analysis_bundle()

    export_job_dashboard = ExportDashboardBundle(quicksight_config, args)
    export_job_dashboard.export_dashboard_bundle()
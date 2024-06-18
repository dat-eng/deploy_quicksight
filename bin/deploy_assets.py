#!/usr/bin/env python

import argparse
import yaml

from import_qs_analysis_bundle import ImportAnalysisBundle
from import_qs_dashboard_bundle import ImportDashboardBundle

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

    import_job_analysis = ImportAnalysisBundle(quicksight_config, args)
    import_job_analysis.import_analysis_bundle()

    import_job_dashboard = ImportDashboardBundle(quicksight_config, args)
    import_job_dashboard.import_dashboard_bundle()
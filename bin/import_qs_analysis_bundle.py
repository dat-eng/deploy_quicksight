#!/usr/bin/env python

import boto3
import os
import time

class ImportAnalysisBundle:

    def __init__(self, quicksight_config, args):

        asset_bundle_directory = quicksight_config['asset_bundle_directory']
        self.import_dir = asset_bundle_directory['analysis_bundle_directory']

        asset = quicksight_config[args.asset_name]
        self.analysis_id = asset['analysis_id']

        if (args.deploy_env == 'prod'):
            import_aws_account = quicksight_config['import_prod_aws_account']
            self.region = import_aws_account['region']
            self.account_id = import_aws_account['account_id']
            self.assume_role_name = import_aws_account['assume_role_name']

        if (args.deploy_env == 'stage'):
            import_aws_account = quicksight_config['import_stage_aws_account']
            self.region = import_aws_account['region']
            self.account_id = import_aws_account['account_id']
            self.assume_role_name = import_aws_account['assume_role_name']

        snowflake_us_east = quicksight_config['snowflake_us_east']
        self.sf_east_host = snowflake_us_east['sf_east_host']
        self.sf_east_db = snowflake_us_east['sf_east_db']
        self.sf_east_wh = snowflake_us_east['sf_east_wh']
        self.sf_east_user_name = snowflake_us_east['sf_east_user_name']
        self.sf_east_password = snowflake_us_east['sf_east_password']

        snowflake_us_west = quicksight_config['snowflake_us_west']
        self.sf_west_host = snowflake_us_west['sf_west_host']
        self.sf_west_db = snowflake_us_west['sf_west_db']
        self.sf_west_wh = snowflake_us_west['sf_west_wh']
        self.sf_west_user_name = snowflake_us_west['sf_west_user_name']
        self.sf_west_password = snowflake_us_west['sf_west_password']

        qs_east_ds = quicksight_config['qs_datasource_east']
        self.qs_ds_east_name = qs_east_ds['qs_ds_east_name']
        self.qs_ds_east_id = qs_east_ds['qs_ds_east_id']

        qs_west_ds = quicksight_config['qs_datasource_west']
        self.qs_ds_west_name = qs_west_ds['qs_ds_west_name']
        self.qs_ds_west_id = qs_west_ds['qs_ds_west_id']

        if (args.local):
            self.target_client = boto3.client('quicksight', region_name=self.region)
        else:
            sts_source = boto3.client('sts')
            resp  = sts_source.assume_role(RoleArn='arn:aws:iam::{}:role/{}'.format(self.account_id, self.assume_role_name),
                        RoleSessionName='AssumeRoleSource')
            target_session = boto3.Session(
                    aws_access_key_id = resp['Credentials']['AccessKeyId'],
                    aws_secret_access_key = resp['Credentials']['SecretAccessKey'],
                    aws_session_token = resp['Credentials']['SessionToken'],
                    region_name = self.region
                )
            self.target_client = target_session.client('quicksight')

        self.analysis_arn = self.get_analysis_arn()
        print('Analysis ARN: {}'.format(self.analysis_arn))

    def get_analysis_arn(self):
        analysis_details = None
        for analysis in self.target_client.list_analyses(AwsAccountId=self.account_id)['AnalysisSummaryList']:
            if analysis['AnalysisId'] == self.analysis_id:
                analysis_details = analysis
                self.analysis_name = analysis['Name']
                self.import_file_name = analysis['Name'].replace(' ', '_').lower()
                self.import_job_id = self.import_file_name
                break

        if analysis_details is None:
            raise NameError("analysis {} not found".format(self.analysis_id))

        return analysis_details['Arn']

    def start_import_job(self):
        bundle_filename = os.path.abspath("{}/{}.zip".format(self.import_dir, self.import_file_name))
        print('Bundle file name:{}'.format(bundle_filename))
        print('Contents of analysis bundles directory:{}'.format(os.listdir(self.import_dir)))
        with open(bundle_filename, 'rb') as f:
            asset_bundle_zip = f.read()
        f.close()

        response = self.target_client.start_asset_bundle_import_job(
            AwsAccountId=self.account_id,
            AssetBundleImportJobId=self.import_job_id,
            AssetBundleImportSource={
                'Body': asset_bundle_zip
            },
            OverrideParameters={
                "DataSources": [
                    {
                        "DataSourceId": self.qs_ds_east_id,
                        "Name": self.qs_ds_east_name,
                        "DataSourceParameters": {
                            "SnowflakeParameters": {
                                "Host": self.sf_east_host,
                                "Database": self.sf_east_db,
                                "Warehouse": self.sf_east_wh
                            }
                        },
                        "SslProperties": {
                            "DisableSsl": False
                        },
                        "Credentials": {
                            "CredentialPair": {
                                "Username": self.sf_east_user_name,
                                "Password": self.sf_east_password
                            }
                        }
                    },
                    {
                        "DataSourceId": self.qs_ds_west_id,
                        "Name": self.qs_ds_west_name,
                        "DataSourceParameters": {
                            "SnowflakeParameters": {
                                "Host": self.sf_west_host,
                                "Database": self.sf_west_db,
                                "Warehouse": self.sf_west_wh
                            }
                        },
                        "SslProperties": {
                            "DisableSsl": False
                        },
                        "Credentials": {
                            "CredentialPair": {
                                "Username": self.sf_west_user_name,
                                "Password": self.sf_west_password
                            } 
                        }
                    }
                ]
            }
        )

        # Retrieve the import job ID
        job_id = response['AssetBundleImportJobId']
        print('Import job started with JobId: {}'.format(job_id))

    def wait_import_job(self):
        # Wait for the import job to complete
        while True:
            print('Waiting for asset bundle import to finish...')
            time.sleep(5)
            response = self.target_client.describe_asset_bundle_import_job(
                AwsAccountId=self.account_id,
                AssetBundleImportJobId=self.import_job_id
            )
            if response['JobStatus'] in ['SUCCESSFUL','FAILED_ROLLBACK_COMPLETED']:
                break

        return response

    def update_permissions(self):
        self.target_client.update_analysis_permissions(
            AwsAccountId=self.account_id,
            AnalysisId=self.analysis_id,
            GrantPermissions=[
                {
                    "Principal": "arn:aws:quicksight:us-east-1:{}:group/default/platform_analytics".format(
                        self.account_id),
                    "Actions": ["quicksight:RestoreAnalysis",
                                "quicksight:UpdateAnalysisPermissions",
                                "quicksight:DeleteAnalysis",
                                "quicksight:DescribeAnalysisPermissions",
                                "quicksight:QueryAnalysis",
                                "quicksight:DescribeAnalysis",
                                "quicksight:UpdateAnalysis"]
                }
            ]
        )

    def import_analysis_bundle(self):

        self.start_import_job()

        response = self.wait_import_job()
        status = response['JobStatus']
        print('Import job status: {}'.format(status))

        if status == 'SUCCESSFUL':
            print('Asset bundle import job complete.')
        elif status == 'FAILED_ROLLBACK_COMPLETED':
            print('Error: {}'.format(response))
            return

        self.update_permissions()
        print('Update permissions analysis completed')

#!/usr/bin/env python

import boto3
import os
import time
import urllib

class ExportAnalysisBundle:

    def __init__(self, quicksight_config, args):

        asset_bundle_directory = quicksight_config['asset_bundle_directory']
        self.analysis_bundle_dir = asset_bundle_directory['analysis_bundle_directory']

        export_aws_account = quicksight_config['export_aws_account']
        self.region = export_aws_account['region']
        self.account_id = export_aws_account['account_id']
        self.assume_role_name = export_aws_account['assume_role_name']

        asset = quicksight_config[args.asset_name]
        self.analysis_id = asset['analysis_id']

        if (args.local):
            self.source_client = boto3.client('quicksight', region_name=self.region)
        else:
            sts_source = boto3.client('sts')
            resp = sts_source.assume_role(RoleArn='arn:aws:iam::{}:role/{}'.format(self.account_id, self.assume_role_name),
                       RoleSessionName='AssumeRoleSource')
            source_session = boto3.Session(
                    aws_access_key_id = resp['Credentials']['AccessKeyId'],
                    aws_secret_access_key = resp['Credentials']['SecretAccessKey'],
                    aws_session_token = resp['Credentials']['SessionToken'],
                    region_name = self.region
                )
            self.source_client = source_session.client('quicksight')

        self.analysis_arn = self.get_analysis_arn()
        print('Analysis ARN: {}'.format(self.analysis_arn))

    def get_analysis_arn(self):
        analysis_details = None
        for analysis in self.source_client.list_analyses(AwsAccountId=self.account_id)['AnalysisSummaryList']:
            if analysis['AnalysisId'] == self.analysis_id:
                analysis_details = analysis
                self.analysis_name = analysis['Name']
                self.export_job_file_name = analysis['Name'].replace(' ', '_').lower()
                self.export_job_id = self.export_job_file_name
                break

        if analysis_details is None:
            raise NameError("analysis {} not found".format(self.analysis_id))

        return analysis_details['Arn']

    def start_export_job(self):
        response = self.source_client.start_asset_bundle_export_job(
            AwsAccountId=self.account_id,
            AssetBundleExportJobId=self.export_job_id,
            ResourceArns=[self.analysis_arn],
            ExportFormat='QUICKSIGHT_JSON',
            IncludeAllDependencies=True
        )

        # Retrieve the export job ID
        job_id = response['AssetBundleExportJobId']
        print('Export job started with JobId: {}'.format(job_id))

    def wait_export_job(self):
        # Wait for the export job to complete
        while True:
            print('Waiting for asset bundle export to finish...')
            time.sleep(5)
            response = self.source_client.describe_asset_bundle_export_job(
                AwsAccountId=self.account_id,
                AssetBundleExportJobId=self.export_job_id
            )
            if response['JobStatus'] in ['SUCCESSFUL','FAILED']:
                break

        return response

    def download_asset_bundle(self, response):
        download_url = response['DownloadUrl']
        bundle_filename =  os.path.abspath("{}/{}.zip".format(self.analysis_bundle_dir, self.export_job_id))
        print('Bundle file name:{}'.format(os.path.abspath(bundle_filename)))
        urllib.request.urlretrieve(download_url, bundle_filename)
        print('Contents of asset bundles directory:{}'.format(os.listdir(self.analysis_bundle_dir)))
        print('Asset bundle downloaded for "{}" analysis'.format(self.analysis_name))

    def export_analysis_bundle(self):

        self.start_export_job()

        response = self.wait_export_job()
        status = response['JobStatus']
        print('Export job status: {}'.format(status))

        if status == 'SUCCESSFUL':
            print('Asset bundle export job complete.')
        elif status == 'FAILED_ROLLBACK_COMPLETED':
            print('Error: {}'.format(response))
            return

        self.download_asset_bundle(response)


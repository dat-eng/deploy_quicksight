# QuickSight

Amazon QuickSight is a cloud-scale business intelligence (BI) service that you can use to deliver easy-to-understand insights to people.

## Environments
We have sandbox & production environments available.

Environment | AWS Account 
---------|-----------
Sandbox | AWS Acct 1
Production  | AWS Acct 2

## Directory Structure

Directory | Description
---------|-----------
asset_bundles | Zip files for Sync sandbox and Deploy (or) Push to production workflows are stored here.
bin     | Python scripts for sync (or) import and fetch (or) export.


## Develop & Deploy

### Tools Used

Tool | Laptop Setup Required? | Description
-----|------------------------|------------
Docker | Yes |Container Software

### Config file

All configuration for deploying dashboards is stored in the *quicksight.yml* file.

### Asset bundle zip file mappings

Dashboard | Dashboard Zip File | Analysis Zip File 
----------|--------------|---------------


### Python Scripts

Script Name | Description
-----|------------------------
fetch_assets.py | Invokes the export scripts listed below
export_qs_analysis_bundle.py | Fetch analysis asset from sandbox
export_qs_dashboard_bundle.py | Fetch dashboard asset from sandbox
deploy_assets.py | Invokes the import scripts listed below
import_qs_analysis_bundle.py | Sync or deploy analysis asset into sandbox or prod
import_qs_dashboard_bundle.py | Sync or deploy dashboard asset into sandbox or prod

### Make file commands 

Dashboard | Sync Command | Fetch Command
----------|--------------|---------------
Usage Trends | ```make sync-sandbox-ut-local``` | ```make fetch-sandbox-ut-local```

### Developer Workflow for Dashboard Update

1. Log into AWS using tool or AWS Configure CLI command. 
2. Pull latest deployed code, and create your branch.
3. Build the docker dev environment using the command:

    ```make build```

4. Sync sandbox with prod version of analysis and dashboard using the dashboard specific make command listed above.

    ```make sync-sandbox-ut-local```

    *Note:*  You can also use the latest release deploy pipeline for the sync.

5. Stage all changes in Sandbox account by directly modifying the analysis via QuickSight UI.
6. Publish the analysis to the dashboard.
7. Fetch the modified asset

   ```make fetch-sandbox-ut-local```

8. Commit the work (zip files) into git and create MR for review
9. After approval, deploy these changes into prod using the latest merged pipeline.

### Reviewer Workflow

1. Sync sandbox from the merge request pipeline

2. Review the changes in sandbox

3. Approve the MR

### Stash Workflow

1. Pull master, and create your branch.
2. Fetch the modified asset

   ```make fetch-sandbox-ut-local```

3. Commit the work (zip files) into git.
4. To continue with the work at a later time, just sync the stashed dashboard from the stowed branch pipeline.



# pager-duty-sync

This application is used for copying data from the pager duty API into S3.

This data can later be synced to other sources (currently only google sheets) by using athena queries to sync data to given endpoints

# Getting started
To get started:

Run: 
```bash
npm i
```

# Test commands
## Test state slack event director with creating google sheets
```
sls step-functions-offline --stage=local --stateMachine=SlackResolver --event="event_payloads\process_slack_event\auth_passed_fill_in_timesheets.json"  
```
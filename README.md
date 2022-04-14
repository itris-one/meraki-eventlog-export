# meraki-eventlog-export
Small python script which downloads the meraki eventlog data as json or csv.

Setup dependencies:
```
pip install -f requirements.txt
```

Example usage:
```
python meraki_events.py -k api-key -n networkid -j events.json -c events.csv
```

Warning, this script downloads the Meraki network event logs in reverse and proceeds until no more events are available. Even with small Networks there logs can easily reach multiple GiB of data

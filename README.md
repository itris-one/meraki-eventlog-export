# Meraki Network Event Log Export
Python CLI script to download all the available meraki network event log data as json and/or csv.

## Use case
The meraki dashboard allows you to view and search through the network event logs very well but the export features are limited. It's not possible to export the events as json and the csv download is limited to the API pagination (1000 rows).

This small script allows you to download events in json (one json object per Line) or csv - beginning from the newest entries until all rows are downloaded or the script is aborted. The json formated export makes further processing easy.

**Warning:** Even with small networks the event logs can easily reach multiple GiB of data.

## Prerequisites
- [Python requirements installed](#Install-dependencies)
- [API Access (API-Key)](#Creating-an-API-Key)
- [Network ID must be known](#Getting-the-network-id)

## Installation

### Clone the repository
```
$ git clone https://github.com/itris-one/meraki-eventlog-export.git
```

**Python version 3** and pip is required. Creating a dedicated virtual environment is recommended.


### Creating a virtual environment (optional)

Install the virtualenv package:
```
$ python -m pip install virtualenv
```

Create and activate a new virtual environment:
```
$ python -m venv ./venv
$ source venv/bin/activate
```

### Install dependencies
```
$ python -m pip install -r requirements.txt
```

## How to Use

```
$ python meraki_events.py --help                                                                                     :(
usage: meraki_events.py [-h] [-k API_KEY] -n NETWORK_ID [-p PRODUCT_TYPE] [-j JSON] [-c CSV] [-v]

Small python script for downloading the meraki eventlog. The events are downloaded in reverse starting from now and proceeds until all events are parsed Example: meraki_events.py
-k MERAKI_API_KEY -n MERAKI_NET_ID -c events.csv

options:
  -h, --help            show this help message and exit
  -k API_KEY, --api-key API_KEY
                        Meraki API Key (X-Cisco-Meraki-API-Key). The env variable MERAKI_API_KEY is used if available
  -n NETWORK_ID, --network-id NETWORK_ID
                        Meraki Network ID. The env variable MERAKI_NET_ID is used if available
  -p PRODUCT_TYPE, --product-type PRODUCT_TYPE
                        Product type filter. Valid types are wireless, appliance, switch, systemsManager, camera, and cellularGateway. Defaults to wireless
  -j JSON, --json JSON  Export as json
  -c CSV, --csv CSV     Export es csv
  -v, --verbose         verbose mode
```

It's possible to stop the download with CTRL + C

### Creating an API-Key
Login to the meraki dashboard, klick on your username and on My Profile. Create a key in the "API Access" category.

Further information in the [meraki API documentation](https://documentation.meraki.com/General_Administration/Other_Topics/The_Cisco_Meraki_Dashboard_API
)

### Getting the network-id

Go to the [get-organizations rest api doc](https://developer.cisco.com/meraki/api/#!get-organizations), click on Configuration and replace the API-Key with yours. Run the get organizations api call and copy your (organization) id from the response data.

Switchover to [get-organizations-networks rest api doc](https://developer.cisco.com/meraki/api/#!get-organization-networks), paste your organization ID and run the request. You will find your network id in the response data as 'id' parameter.

## Examples : 
Getting all wireless network events from the DevNet Sandbox as CSV and JSON:
```
$ python meraki_events.py -k 6bec40cf957de430a6f1f2baa056b99a4fac9ea0 -n L_566327653141843049 -c events.csv -j events.json
Requesting page 1 (before None)
Requesting page 2 (before 2022-04-24T12:33:06.173307Z)
Requesting page 3 (before 2022-04-23T16:54:04.069118Z)
Requesting page 4 (before 2022-04-22T18:40:49.189759Z)
Requesting page 5 (before 2022-04-21T19:02:21.291898Z)
Requesting page 6 (before 2022-04-20T18:56:04.950773Z)
[...]
```

Using environment variables instead of arguments:
```
$ export MERAKI_API_KEY=6bec40cf957de430a6f1f2baa056b99a4fac9ea0
$ export MERAKI_NET_ID=L_566327653141843049
$ python meraki_events.py -j events.json -c events.csv
```

## JSON Sample
```
{"occurredAt": "2022-04-25T14:01:29.527781Z", "networkId": "L_566327653141843049", "type": "disassociation", "description": "802.11 disassociation", "clientId": "kd9a3d9", "clientDescription": "Shannons-MacBook-Air", "deviceSerial": "Q2LD-ZWCZ-XXXX", "deviceName": "Office AP", "ssidNumber": 0, "ssidName": "Lyoli", "eventData": {"radio": "0", "vap": "0", "client_mac": "D0:81:7A:XX:XX:XX", "channel": "1", "duration": "307.433531520", "auth_neg_dur": "0.005865440", "last_auth_ago": "307.424017760", "is_wpa": "1", "full_conn": "11.628742560", "ip_resp": "11.628742560", "aid": "1082159969"}}
{"occurredAt": "2022-04-25T13:56:52.101206Z", "networkId": "L_566327653141843049", "type": "disassociation", "description": "802.11 disassociation", "clientId": "kd9a3d9", "clientDescription": "Shannons-MacBook-Air", "deviceSerial": "Q2LD-ZWCZ-XXXX", "deviceName": "Office AP", "ssidNumber": 0, "ssidName": "Lyoli", "eventData": {"radio": "1", "vap": "0", "client_mac": "D0:81:7A:XX:XX:XX", "client_ip": "192.168.1.123", "channel": "36", "duration": "13134.308962720", "auth_neg_dur": "0.008090560", "last_auth_ago": "13134.295676800", "is_wpa": "1", "full_conn": "0.219878400", "ip_resp": "0.219878400", "ip_src": "192.168.1.123", "http_resp": "1.642622880", "arp_resp": "0.060223520", "arp_src": "192.168.1.123", "dns_req_rtt": "0.005631840", "dns_resp": "0.174638400", "dhcp_lease_completed": "0.063866560", "dhcp_ip": "192.168.1.123", "dhcp_server": "192.168.1.123", "dhcp_server_mac": "10:93:97:XX:XX:XX", "dhcp_resp": "0.063866560", "aid": "1468840567"}}
{"occurredAt": "2022-04-25T13:56:22.112345Z", "networkId": "L_566327653141843049", "type": "wpa_auth", "description": "WPA authentication", "clientId": "kd9a3d9", "clientDescription": "Shannons-MacBook-Air", "deviceSerial": "Q2LD-ZWCZ-XXXX", "deviceName": "Office AP", "ssidNumber": 0, "ssidName": "Lyoli", "eventData": {}}
{"occurredAt": "2022-04-25T13:56:22.106483Z", "networkId": "L_566327653141843049", "type": "association", "description": "802.11 association", "clientId": "kd9a3d9", "clientDescription": "Shannons-MacBook-Air", "deviceSerial": "Q2LD-ZWCZ-XXXX", "deviceName": "Office AP", "ssidNumber": 0, "ssidName": "Lyoli", "eventData": {"channel": "1", "rssi": "59"}}
{"occurredAt": "2022-04-25T13:50:18.069197Z", "networkId": "L_566327653141843049", "type": "aps_association_reject", "description": "802.11 association rejected for client balancing", "clientId": "kfadf16", "clientDescription": "android-384d36fc4262XXXX", "deviceSerial": "Q2LD-GYL3-XXXX", "deviceName": "1st Floor AP", "eventData": {"load": "3", "best_ap": "192.168.1.95", "best_ap_load": "0", "best_ap_rssi": "40"}}
```

## CSV Sample
```
ccurredAt,networkId,type,description,clientId,clientDescription,deviceSerial,deviceName,ssidNumber,ssidName,eventData
2022-04-25T14:01:29.527781Z,L_566327653141843049,disassociation,802.11 disassociation,kd9a3d9,Shannons-MacBook-Air,Q2LD-ZWCZ-XXXX,Office AP,0,Lyoli,"{'radio': '0', 'vap': '0', 'client_mac': 'D0:81:7A:XX:XX:XX', 'channel': '1', 'duration': '307.433531520', 'auth_neg_dur': '0.005865440', 'last_auth_ago': '307.424017760', 'is_wpa': '1', 'full_conn': '11.628742560', 'ip_resp': '11.628742560', 'aid': '1082159969'}"
2022-04-25T13:56:52.101206Z,L_566327653141843049,disassociation,802.11 disassociation,kd9a3d9,Shannons-MacBook-Air,Q2LD-ZWCZ-XXXX,Office AP,0,Lyoli,"{'radio': '1', 'vap': '0', 'client_mac': 'D0:81:7A:XX:XX:XX', 'client_ip': '192.168.1.166', 'channel': '36', 'duration': '13134.308962720', 'auth_neg_dur': '0.008090560', 'last_auth_ago': '13134.295676800', 'is_wpa': '1', 'full_conn': '0.219878400', 'ip_resp': '0.219878400', 'ip_src': '192.168.1.123', 'http_resp': '1.642622880', 'arp_resp': '0.060223520', 'arp_src': '192.168.1.123', 'dns_req_rtt': '0.005631840', 'dns_resp': '0.174638400', 'dhcp_lease_completed': '0.063866560', 'dhcp_ip': '192.168.1.123', 'dhcp_server': '192.168.1.123', 'dhcp_server_mac': '10:93:97:XX:XX:XX', 'dhcp_resp': '0.063866560', 'aid': '1468840567'}"
2022-04-25T13:56:22.112345Z,L_566327653141843049,wpa_auth,WPA authentication,kd9a3d9,Shannons-MacBook-Air,Q2LD-ZWCZ-XXXX,Office AP,0,Lyoli,{}
2022-04-25T13:56:22.106483Z,L_566327653141843049,association,802.11 association,kd9a3d9,Shannons-MacBook-Air,Q2LD-ZWCZ-XXXX,Office AP,0,Lyoli,"{'channel': '1', 'rssi': '59'}"
2022-04-25T13:50:18.069197Z,L_566327653141843049,aps_association_reject,802.11 association rejected for client balancing,kfadf16,android-384d36fc4262XXXX,Q2LD-GYL3-XXXX,1st Floor AP,,,"{'load': '3', 'best_ap': '192.168.1.123', 'best_ap_load': '0', 'best_ap_rssi': '40'}"
```

[![published](https://static.production.devnetcloud.com/codeexchange/assets/images/devnet-published.svg)](https://developer.cisco.com/codeexchange/github/repo/itris-one/meraki-eventlog-export)

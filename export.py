import logging as log
import json
import requests
import csv
import time
import argparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

PAGE_SIZE = 1000


def readPage(re, baseURL, endingBefore=None, pageSize=1000, **params):
  params["perPage"] = pageSize
  if endingBefore:
    params["endingBefore"] = endingBefore

  try:
    response = re.get(baseURL, params=params)
  except requests.exceptions.ConnectionError:
    print("Connection Error, retry in 10s")
    time.sleep(10)
    return readPage(re, baseURL, pageSize=pageSize, **params)    

  if response.status_code == 200:
    page = response.json()
    return page["events"], page['pageStartAt'], page['pageEndAt'], len(page["events"]) == pageSize

  elif response.status_code == 429:
    print("API Limit reached, wait %ss" % response.headers["Retry-After"])
    time.sleep(int(response.headers["Retry-After"]))
    return readPage(re, baseURL, pageSize=pageSize, **params)



if __name__ == "__main__":
  
    parser = argparse.ArgumentParser(description="""Small python script for downloading the meraki eventlog. The events are downloaded in reverse starting from now and proceeds until all events are parsed
    Example: meraki_events.py -k MERAKI_API_KEY
""")

    parser.add_argument('-k', '--api-key', help='Meraki API Key (X-Cisco-Meraki-API-Key)', default=os.environ.get("MERAKI_API_KEY"))
    parser.add_argument('-n', '--network-id', help='Meraki Network ID', default=os.environ.get("MERAKI_NET_ID"))
    parser.add_argument('-v', '--verbose', action='store_const', const=True, help='verbose mode')
    parser.add_argument('-j', '--json', help='Export as json')
    parser.add_argument('-c', '--csv', help='Export es csv')

    args = parser.parse_args()
  
  
  re = requests.Session()
  re.headers['X-Cisco-Meraki-API-Key'] = args.api_key

  retries = Retry(total=5, backoff_factor=5, status_forcelist=[ 502, 503, 504 ])
  re.mount('http://', HTTPAdapter(max_retries=retries))


  if args.verbose:
      log.basicConfig(level=log.DEBUG)
      
  if not args.api_key or not args.network_id:
        parser.print_help()
        exit(1)

  startAt = None
  fullPage = True
  pageNum = 0
  
  neJSON = None
  
  if args.json:
    neJSON = open(OUTPUT_NETEVENTS_JSON, "w")

  neCSV  = None
  neCSVwriter = None
  
  if args.csv:
    neCSV  = open(OUTPUT_NETEVENTS_CSV, "w")

    fieldnames = ["occurredAt", "networkId", "type", "description", "clientId", "clientDescription", "deviceSerial", "deviceName", "ssidNumber", "ssidName", "eventData"]
    neCSVwriter = csv.DictWriter(neCSV, fieldnames=fieldnames)
    neCSVwriter.writeheader()

  eventCount = 0
  while fullPage:
    pageNum += 1

    print("## Request Page %s (before %s)" % (pageNum, startAt))
    pageEvents, startAt, endAt, fullPage = readPage(re, "https://api.meraki.com/api/v1/networks/%s/events" % args.network_id, productType="wireless", pageSize=PAGE_SIZE, endingBefore=startAt)

    eventCount += len(pageEvents)

    if args.json:
      neJSON.write(json.dumps(pageEvents) + "\n")
      neJSON.flush()

    if args.csv:
      for e in pageEvents:
        neCSVwriter.writerow(e)
      neCSV.flush()


  if args.json:
    neJSON.close()
  if args.csv:
    neCSV.close()

  print("Exported %s Events" % eventCount)

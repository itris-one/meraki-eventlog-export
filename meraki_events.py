import logging as log
import json
import requests
import csv
import time
import argparse
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
import os


PAGE_SIZE = 1000

def readPage(re, baseURL, endingBefore=None, pageSize=1000, **params):
  """Helper function for handling http retries and pagination parameters"""
  params["perPage"] = pageSize
  if endingBefore:
    params["endingBefore"] = endingBefore

  try:
    response = re.get(baseURL, params=params)
  except requests.exceptions.ConnectionError:
    log.warning("Connection error, retry in 10s")
    time.sleep(10)
    return readPage(re, baseURL, pageSize=pageSize, **params)    

  if response.status_code == 200:
    page = response.json()
    return page["events"], page['pageStartAt'], page['pageEndAt'], len(page["events"]) == pageSize

  elif response.status_code == 429:
    log.warning("API limit reached, wait %ss" % response.headers["Retry-After"])
    time.sleep(int(response.headers["Retry-After"]))
    return readPage(re, baseURL, pageSize=pageSize, **params)
  
  elif response.status_code == 404: # Eventlog is empty
    log.error("Invalid network-id")
    exit(1)
  elif response.status_code == 401:
    log.error("Authentication failed, is the api-key correct?")
    exit(1)
  else:
    log.error("Unhandled status code %s" % (response.status_code))
    exit(1)



if __name__ == "__main__":
  
  parser = argparse.ArgumentParser(description="""Small python script for downloading the meraki eventlog. The events are downloaded in reverse starting from now and proceeds until all events are parsed
  Example: meraki_events.py -k MERAKI_API_KEY -n MERAKI_NET_ID -c events.csv
""")

  parser.add_argument('-k', '--api-key', help='Meraki API Key (X-Cisco-Meraki-API-Key). The env variable MERAKI_API_KEY is used if available',
                      default=os.environ.get("MERAKI_API_KEY"), required=os.environ.get("MERAKI_API_KEY")==None)
  
  parser.add_argument('-n', '--network-id', help='Meraki Network ID. The env variable MERAKI_NET_ID is used if available',
                      default=os.environ.get("MERAKI_NET_ID"),  required=os.environ.get("MERAKI_NET_ID")==None)
  
  parser.add_argument('-p', '--product-type', help='Product type filter. Valid types are wireless, appliance, switch, systemsManager, camera, and cellularGateway. Defaults to wireless', default="wireless")
  
  parser.add_argument('-j', '--json', help='Export as json')
  parser.add_argument('-c', '--csv', help='Export es csv')
  parser.add_argument('-v', '--verbose', action='store_const', const=True, help='verbose mode')
    
  args = parser.parse_args()
  
  re = requests.Session()
  re.headers['X-Cisco-Meraki-API-Key'] = args.api_key

  retries = Retry(total=5, backoff_factor=5, status_forcelist=[ 502, 503, 504 ])
  re.mount('http://', HTTPAdapter(max_retries=retries))


  if args.verbose:
      log.basicConfig(level=log.DEBUG)
        
  if not args.json and not args.csv:
    parser.print_help()
    
    print("\nat least one export type is required\n")
    exit(1)

  startAt = None
  fullPage = True
  pageNum = 0
  
  neJSON = None
  
  if args.json:
    neJSON = open(args.json, "w")

  neCSV  = None
  neCSVwriter = None
  
  if args.csv:
    neCSV  = open(args.csv, "w")

    fieldnames = ["occurredAt", "networkId", "type", "description", "clientId", "clientDescription", "deviceSerial", "deviceName", "ssidNumber", "ssidName", "eventData"]
    neCSVwriter = csv.DictWriter(neCSV, fieldnames=fieldnames)
    neCSVwriter.writeheader()

  eventCount = 0

  try:
    while fullPage: # Continue as long as the number of results is equal to the page size.
      pageNum += 1

      print("Requesting page %s (before %s)" % (pageNum, startAt))
      # API Documentation: https://developer.cisco.com/meraki/api/#!get-network-events
      pageEvents, startAt, endAt, fullPage = readPage(re, "https://api.meraki.com/api/v1/networks/%s/events" % args.network_id, productType=args.product_type, pageSize=PAGE_SIZE, endingBefore=startAt)

      eventCount += len(pageEvents)


      for event in pageEvents:
        if args.json:
          neJSON.write(json.dumps(event) + "\n")
        if args.csv:
          neCSVwriter.writerow(event)


      if args.json: neJSON.flush()
      if args.csv: neCSV.flush()

  except KeyboardInterrupt:
    print("\nEvent download aborted")


  if args.json:
    neJSON.close()
  if args.csv:
    neCSV.close()

  if eventCount == 0:
    print("No events found on this network")
  else:
    print("Exported %s events" % eventCount)

import datetime, math
import pandas as pd
from sodapy import Socrata
from twilio.rest import Client

import json
import time
import urllib
import urllib.request as request

# address = "65-30 Kissena Blvd, Flushing, NY 11367"
address = "184-44 Grand Central Parkway, Jamaica NY"
recipient_phone = "+15635427998"

def get_coords(address):
  print("getting coordinates")
  maps_key = 'AIzaSyCWtzKWLugogOt4IhWfW7p9jWIsENZ9f9E'
  base_url = 'https://maps.googleapis.com/maps/api/geocode/json'

  # This joins the parts of the URL together into one string.
  url = base_url + '?' + urllib.parse.urlencode({
    'address': "+".join(address.split()),
    'key': maps_key,
  })

  current_delay = 0.1  # Set the initial retry delay to 100ms.
  # max_delay = 3600  # Set the maximum retry delay to 1 hour.
  max_delay = 60

  while True:
    try:
      # Get the API response.
      response = request.urlopen(url).read().decode('utf-8')
    except IOError:
      pass  # Fall through to the retry loop.
    else:
      # If we didn't get an IOError then parse the result.
      # result = json.loads(response.replace('\\n', ''))
      result = json.loads(response)
      if result['status'] == 'OK':
        # return result['timeZoneId']
        return result['results'][0]['geometry']['location']
      elif result['status'] != 'UNKNOWN_ERROR':
        # Many API errors cannot be fixed by a retry, e.g. INVALID_REQUEST or
        # ZERO_RESULTS. There is no point retrying these requests.
        raise Exception(result['error_message'])

    if current_delay > max_delay:
      raise Exception('Too many retry attempts.')
    print('Waiting', current_delay, 'seconds before retrying.')
    time.sleep(current_delay)
    current_delay *= 2  # Increase the delay each time we retry.

coords = get_coords(address)
print(coords)

# my_latitude = 40.737974
# my_longitude = -73.817239
my_latitude = coords["lat"]
my_longitude = coords["lng"]
latitude_in_miles = 69.172
longitude_in_miles = math.cos(my_latitude) * latitude_in_miles
latitude_range = abs(1 / (latitude_in_miles))
longitude_range = abs(1 / (longitude_in_miles))

socrata_client = Socrata("data.cityofnewyork.us", "WggC6GQY8QfRsyCkL1Lr6HR2M")

time_range = datetime.datetime.utcnow() - datetime.timedelta(days = 7)
time_query = "created_date > '" + time_range.isoformat() + "'"
results = socrata_client.get("fhrw-4uyv", where=time_query)

df = pd.DataFrame.from_records(results)

message_body = ""
complaint_sum = 0
for row in df.itertuples():
	latitude = float(row.latitude)
	longitude = float(row.longitude)
	if (latitude < my_latitude + latitude_range and latitude > my_latitude - latitude_range and 
		longitude < my_longitude + longitude_range and longitude > my_longitude - longitude_range):
		complaint_sum += 1
		message_body += "Complaint #" + str(complaint_sum) + ":\n"
		message_body += str(row.incident_address) + "\n"
		message_body += "Type: " + row.complaint_type + "\n"
		message_body += "Descriptor: " + row.descriptor + "\n"
		message_body += "\n"

message_body = "A total of " + str(complaint_sum) + " 311 complaints were made within one mile of your address in the last week.\n\n" + message_body
print(message_body)

twilio_client = Client("AC97d355e4de17b0b271417ba6dbcff301", "157612460b29f759b6ca6d437427483b")
message = twilio_client.messages.create(
    to=recipient_phone,
    from_="+16202061129",
    body=message_body)

print("OK")

import json
import time
import urllib
import urllib.request as request

def get_coords(address):
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

address = "65-30 Kissena Blvd, Flushing, NY 11367"

coords = get_coords(address)

print(coords)


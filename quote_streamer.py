# Version 3.6.1
import sys
import requests
import json
from tia.auth import *
from tia.log import *
from retry import retry

# CAN BE REMOVED, FROM HERE -
import time
import threading
# TILL HERE

class Streamer:
  _headers = {'Accept': 'application/json'}
  _URL = 'https://stream.tradier.com/v1/markets/events'
  _resubscribe = False
  _callback = None
  _running = False

  def __sessionKey(self):
    try:
      response = requests.post('https://api.tradier.com/v1/markets/events/session',
        data={},
        headers=getAuthHeader()
      )
      json_response = response.json()
      session_id = json_response['stream']['sessionid']
    except Exception as e:
      log().critical(str(e), ", STATUS_CODE : ", response.status_code)
    return session_id


  @retry(delay=1, backoff=2, tries=3)
  def subscribe(self, symbols, callback):
    self._running = True
    self._callback = callback
    session_key = self.__sessionKey()
    log().info("Successfully obtained the session key for streaming")
    payload = {
      'sessionid': session_key,
      'symbols': symbols,
      'linebreak': True,
      'validOnly' : True,
    }
    log().info("Now subscribing to quotes")
    r = requests.post(self._URL, stream=True, data=payload, headers=self._headers )

    if (r.status_code != 200):
      log().error("Error while subscribing to the data, STATUS_CODE :" + str(r.status_code) )
      raise Exception("Error while subscribing to the data, STATUS_CODE :", r.status_code)

    log().info("Subscription successful, STATUS_CODE :" + str(r.status_code))
    # Now Iterate through the quotes
    try:
      for line in r.iter_lines():
        if (self._resubscribe):
          log().info("Existing as resubscribe flag is True" )
          print("Existing as resubscribe flag is True")
          self._resubscribe = False
          self._running = False
          return
        if line:
            self._callback(line)
    except Exception as e:
      log().error("Received an exception while parsing subscription : " + str(e))
      raise e

  # Subscribes if not alreayd subscribed else resubscribes
  def resubscribe(self,symbols, callback = None):
    if (self._running == True):
      self._resubscribe = True
      while( self._running != False):
        continue
      print("******FINALLY EXITED*****")
      callback = self._callback
    self.subscribe(symbols,callback)


def example():
  s = Streamer()
  def handler(line):
    print (line)
    return
    json_formatted_str = json.dumps(json.loads(line), indent=2)
    x = json.loads(line)
    if (x['type'] == 'trade'):
      print(json_formatted_str)
    if (x['type'] == 'timesale'):
      print(json_formatted_str)
      #log().info(line)
    if (x['type'] == 'quote'):
      print(json_formatted_str)
      #log().info(line)
  def a(g):
      print("Function a is running at time: " + str(int(time.time())) + " seconds." + g)
      time.sleep(5)
      print("HAHAHAHAHAHAHAH******************** RESUBSCRIBIBNG")
      s.resubscribe('GOOG,NKLA')
  threading.Thread(target=a,args=('d',)).start()

  s.subscribe("SPY",handler)
  time.sleep(5)
  print("HGAHAHAH")

if __name__ == '__main__':
  example()

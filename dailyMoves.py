import history as historyUtil
import sys
import datetime


# Returns the avg max % change ( highest - lowest) / Open, over the specified daysBack
def printHistory(symbol, daysBack = 30 * 12 * 10):
  today = datetime.date.today()
  timedelta = datetime.timedelta(daysBack)
  start_date = today - timedelta

  data = historyUtil.getHistory(symbol, 'daily', start_date)
  for d in data['history']['day']:
    print (d)

  total_days = len(data['history']['day']) - 1 # -1 to exclude today's date
  days_left = total_days
  avg_change = 0
  for day in data['history']['day']:
    if (days_left <= 0):
      break
    highest_diff = 100*(day['high'] - day['low'])/day['open']
    highest_diff = float("{:.2f}".format(highest_diff))
    print(day['date'] , day['open'], "{:.2F}".format(day['high'] - day['low']), str(highest_diff)  + "%")
    avg_change = avg_change + highest_diff
    days_left = days_left - 1
  res = float("{:.2F}".format(avg_change/total_days))
  print(res)
  return res




if __name__ == '__main__':
  printHistory(sys.argv[1], 10)
#print(movement1m(sys.argv[1], 10, 10))

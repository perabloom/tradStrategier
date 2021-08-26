import json
file1 = open('WISH', 'r',)

bull = 0
bear = 0
for line in file1:
    js = json.loads(line[2:-2])

    if (js['type'] == 'timesale'):
        mid = float(js['bid']) + float(js['ask'])
        mid= mid / 2.0
        last = float(js['last'])
        if (mid > last):
            bull += int(js['size'])
        else:
            bear += int(js['size'])

print( bull, bear, bull / (bull + bear))

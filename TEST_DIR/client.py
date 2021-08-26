import httplib, subprocess

# https://stackoverflow.com/questions/33662842/simple-python-server-to-process-get-and-post-requests-with-json

c = httplib.HTTPConnection('localhost', 8080)
c.request('POST', '/return', '{}')
doc = c.getresponse().read()
print(doc)

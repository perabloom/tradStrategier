import time

print('I am a time() method: {}'.format(time.time()))
print('I am the perf_counter() method: {}'.format(time.perf_counter()))
print('I am the process_time() method: {}'.format(time.process_time()))
t0 = time.time()
c0 = time.perf_counter()
p0 = time.process_time()
r = 0
for i in range(10):
    print("SENDING MESSAGE")
print(r)
t1 = time.time()
c1 = time.perf_counter()
p1 = time.process_time()
spend1 = t1 - t0
spend2 = c1 - c0
spend3 = p1 - p0
print("Time() method takes time: {}s".format(spend1))
print("perf_counter() time: {}s".format(spend2))
print("process_time() time: {}s".format(spend3))
print("Test completed")

file1 = open('/Users/vjain1/Personal/Tradier/Sandbox/TEST_DIR/FROM_CRON', 'a',)
file1.write("WRITING THIS RUN")
file1.close()

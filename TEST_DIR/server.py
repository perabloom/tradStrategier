from bottle import route, run
import timesale as timesaleUtil

@route('/ticks/<name>')
def ticks(name):
    print(name)
    arg = {name}
    response =  timesaleUtil.example(arg)
    return {'response': response}
    #return "Hello World!"

run(host='192.168.1.12', port=8080, debug=True)



#https://bottlepy.org/docs/dev/tutorial.html
# https://stackoverflow.com/questions/33662842/simple-python-server-to-process-get-and-post-requests-with-json

from flask import Flask,url_for ,request ,json , Response ,jsonify
from functools import wraps
import logging
app=Flask(__name__)
file_handler = logging.FileHandler('app.log')
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.INFO)

def check_auth(user,password):
    return user == "admin" and password=="admin"

def autenticate():
    message = {"message":"autenthicate"}
    resp = jsonify(message)
    resp.status_code = 401
    resp.header["WWW-authencticate"]='Basic realm ="example"'
    return resp

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth:
            return autenticate()
        elif not check_auth(auth.username,auth.password):
            return autenticate()
        return f(*args, **kwargs)
    
    return decorated

@app.route("/")
@requires_auth
def api_root():
    if "name" in request.args:
        return 'Hello' + request.args['name']
    else:
        return "Hello john doe"

@app.route("/articles")
def api_articles():
    return 'List of'+ url_for("api_articles")

@app.route("/articles/<articleid>")
def api_article(articleid):
    return "You are reading" + articleid

@app.route("/echo",methods=['GET',"POST","PATCH","PUT","DELETE"])
def api_echo():
    if request.method == 'GET':
        return "ECHO: GET\n"

    elif request.method == 'POST':
        return "ECHO: POST\n"

    elif request.method == 'PATCH':
        return "ECHO: PACTH\n"

    elif request.method == 'PUT':
        return "ECHO: PUT\n"

    elif request.method == 'DELETE':
        return "ECHO: DELETE"
    
@app.route("/messages",methods = ["POST"])
def api_message():
    
    if request.headers["Content-Type"]== 'text/plain':
        return "Text messgae" + request.data
    
    elif request.headers['Content-Type'] == 'application/json':
        return "JSON Message: " + json.dumps(request.json)

    elif request.headers['Content-Type'] == 'application/octet-stream':
        f = open('./binary', 'wb')
        f.write(request.data)
        f.close()
        return "Binary message written!"

    else:
        return "415 Unsupported Media Type ;)"

@app.route("/hello",methods=['GET'])
def api_hello():
    data={
        'Hello':"World",
        'number':3
    }
    #js = json.dumps(data)
    #res = Response(js,status=200,mimetype="applicaton/json")
    #res.headers['Link']="google.com"
    res = jsonify(data)
    res.status_code=200
    #app.logger.info('informing')
    #app.logger.warning('warning')
    #app.logger.error('screaming bloody murder!')
    return res

@app.errorhandler(404)
def not_found(error=None):
    message ={
        'status':404,
        'Message': "not found" + request.url,
    }
    res = jsonify(message)
    res.status_code=404
    return res

@app.route('/users/<userid>', methods = ['GET'])
def api_users(userid):
    users = {'1':'john', '2':'steve', '3':'bill'}
    
    if userid in users:
        return jsonify({userid:users[userid]})
    else:
        return not_found()

if __name__=="__main__":
    app.run()
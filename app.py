from flask import Flask
from flask import request
from flask import session, redirect, jsonify, render_template
from functools import wraps
import json
import dictToXML


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False

app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'
index_count = 0
bool_logout = False


def authorization(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        if session.get('logged_in'):
            return func(*args, **kwargs)
        else:
            return redirect('/login')
    return decorated



@app.route('/login', methods = ['POST','GET'])
def logowanie():
	if request.method == "POST":
		username = 'TRAIN'
		password = 'TuN3L'
		auth = request.authorization
		if username == auth.username and password == auth.password:
			session['logged_in'] = True
			return redirect('/hello')
		else:
			 return jsonify({"message": "ERROR: Unauthorized"}), 401
	else:
		return jsonify({"message": "ERROR: Unauthorized"}), 401

@app.route('/hello')
@authorization
def hello():
	print(session['logged_in'])
	return render_template('templates.html',user = request.authorization.username)


@app.route('/logout', methods = ['POST'])
@authorization
def wylogowanie():
	if session.get('logged_in') == True:
		session['logged_in'] = False
		return redirect('/')
	else:
		return redirect('/login')

@app.route("/trains", methods = ['POST','GET'])
@authorization
def trains():
	if request.method == "POST":
		with open('resources/trains.json', 'r') as f:
			try:
				data = json.load(f)
			except:
				data = None
		request_data = request.get_json(force=True)
		print(request_data)
		if data is None:
			data = dict()
			data["uuid_" + str(1)] = request_data
		else:
			trains_count = len(data)
			data["uuid_" + str(trains_count+1)] = request_data
		with open('resources/trains.json', 'w') as f:
			json.dump(data, f)
		return redirect('/trains/'+str(trains_count+1)+'?format=json')
	if request.method == "GET":
		with open('resources/trains.json', 'r') as f:
			data = json.load(f)
		data_format = request.args.get('format')
		if data_format == 'json':
			return jsonify(data)
		else:
			return jsonify(data)



@app.route('/trains/<id>', methods=['GET', 'DELETE'])
@authorization
def trains5(id):
	if 'u' not in id: id ='uuid_' + str(id)
	with open('resources/trains.json', 'r') as f:
			data = json.load(f)
	if request.method == "GET":
		data_format = request.args.get('format')
		if data_format == 'json':
			return jsonify(data[id])
		else:
			return dictToXML.dict_to_xml(data["uuid_"+int(id)])
	elif request.method == "DELETE":
		print ('hahah')
		del data[id]
		with open('resources/trains.json', 'w') as f:
			json.dump(data, f)
		return jsonify({"message": ""}), 204

@app.route('/')
def main():
    return "hello"

if __name__ == '__main__':
    app.run(debug=True)
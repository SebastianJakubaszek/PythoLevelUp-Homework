from flask import Flask, request, jsonify, g
import sqlite3


app = Flask(__name__)
app.config['JSON_AS_ASCII'] = False
DATABASE = 'resources/chinook.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()
		

@app.route('/tracks', methods=['GET','POST'])
def tracks():
	if request.method == "GET":
		db = get_db()
		db.row_factory = lambda cursor, row: row[0]
		cursor = db.cursor()
		artist = request.args.get('artist')
		per_page = request.args.get('per_page')
		page = request.args.get('page')
		if artist is None:
			if per_page is None:
				data = cursor.execute('SELECT name FROM tracks ORDER BY name COLLATE NOCASE').fetchall()
			else:
				if page is None:
					data = cursor.execute(
						'SELECT name FROM tracks ORDER BY name COLLATE NOCASE LIMIT :per_page',
						{'per_page': per_page, 'offset': offset}).fetchall()
				else:
					offset = (int(page) - 1) * int(per_page)
					data = cursor.execute(
						'SELECT name FROM tracks ORDER BY name COLLATE NOCASE LIMIT :per_page OFFSET :offset',
						{'per_page': per_page, 'offset': offset}).fetchall()
			cursor.close()
			return jsonify(data)
		else:
			if per_page is None:
				data = cursor.execute(
					'SELECT tracks.name FROM tracks' 
					'JOIN albums ON tracks.albumid = albums.albumid'
					'JOIN artists ON albums.artistid = artists.artistid'
					'WHERE artists.name = :artist ORDER BY tracks.name COLLATE NOCASE ',
					{'artist': artist}).fetchall()

			else:
				if page is None:
					data = cursor.execute(
						'SELECT tracks.name FROM tracks'
						'JOIN albums ON tracks.albumid = albums.albumid'
						' JOIN artists ON albums.artistid = artists.artistid'
						'WHERE artists.name = :artist ORDER BY tracks.name COLLATE NOCASE LIMIT :per_page',
						{'artist': artist, 'per_page': per_page}).fetchall()
				else:
					offset = (int(page)-1)*int(per_page)
					data = cursor.execute(
						'SELECT tracks.name FROM tracks '
						'JOIN albums ON tracks.albumid = albums.albumid'
						'JOIN artists ON albums.artistid = artists.artistid'
						'WHERE artists.name = :artist ORDER BY tracks.name COLLATE NOCASE LIMIT :per_page OFFSET :offset',
						{'artist': artist,'per_page': per_page, 'offset': offset}).fetchall()
			return jsonify(data)
			
			
	else:
		if(request.data):
			if request.is_json:
				data = request.get_json(force=True)
				list = ["album_id","media_type_id","genre_id","name","composer","milliseconds","bytes","price"]
				for i in list:
					if i not in data:
						return "", 400
				db = get_db()
				cursor = db.cursor()
				album_id = data['album_id']
				media_type_id = data['media_type_id']
				name = data['name']
				composer = data['composer']
				genre_id = data['genre_id']
				milliseconds = data['milliseconds']
				bytes = data['bytes']
				price = data['price']
				db.execute(
					 'INSERT INTO tracks (albumid,mediatypeid,genreid,name,composer,milliseconds,bytes,unitprice)'
					 'VALUES (?,?,?,?,?,?,?,?)', (album_id, media_type_id, genre_id, name, composer, milliseconds, bytes, price)
				)
				db.commit()
				track_id = cursor.execute('SELECT trackid FROM tracks ORDER by trackid DESC ').fetchone()
				track_id = track_id[0]
				data["track_id"] = track_id
				return jsonify(data)
			else:
				return "", 400
		else:
			return "", 400

@app.route('/genres')
def genres():
	db = get_db()
	cursor = db.cursor()
	db.row_factory = lambda cursor, row: row[0]
	data = db.execute('SELECT name FROM genres ORDER BY name').fetchall()
	dict={}
	for nazwa in data:
		count = cursor.execute(
			'SELECT count(genres.name) FROM tracks'
			'JOIN genres ON genres.genreid = tracks.genreid WHERE genres.name == :cos',
			{'cos': nazwa} ).fetchone()
		dict[nazwa] = count[0]
	return jsonify(dict)

	
if __name__ == '__main__':
    app.run(debug=True)
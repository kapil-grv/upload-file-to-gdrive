from __future__ import print_function
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from apiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaFileUpload

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
db = SQLAlchemy(app)

SCOPES = 'https://www.googleapis.com/auth/drive'
store = file.Storage('credentials.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
drive_service = build('drive', 'v3', http=creds.authorize(Http()))


def uploadFile(filename, filetype):
    file_metadata = {'name': filename + '.' + filetype, 'mimeType': '*/*'}
    media = MediaFileUpload(filename + '.' + filetype,
                            mimetype='*/*',
                            resumable=True)
    file = drive_service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(filename + '.' + filetype)
    print('File ID: ' + file.get('id'))


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.String(500), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    file_format = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return '<Task %r>' % self.id


@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        try:
            return redirect('/')
        except:
            return 'There was an issue adding your file'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('index.html', tasks=tasks)


@app.route('/upload', methods=['POST', 'GET'])
def uploadPage():
    if request.method == 'POST':
        try:
            return redirect('/')
        except:
            return 'There was an issue adding your file'

    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template('upload.html', tasks=tasks)


@app.route('/uploader', methods=['GET', 'POST'])
def upload():
    now = datetime.now()
    ts = datetime.timestamp(now)
    uploadId = int(str(ts).split('.')[0])
    new_task = Todo(id=uploadId)

    if request.method == 'POST':
        new_task.name = request.form['name']
        new_task.description = request.form['description']
        new_task.file_format = request.form['file_format']
        uploadedFile = request.files['fileUpload']
        uploadedFile.save(uploadedFile.filename)

        try:
            uploadFile(request.form['name'], request.form['file_format'])
            db.session.add(new_task)
            db.session.commit()
            return redirect('/')
        except Exception as e:
            print(e)
            return 'There was an issue uploading your file'

    else:
        return render_template('index.html', task=new_task)


if __name__ == "__main__":
    app.run(debug=True)

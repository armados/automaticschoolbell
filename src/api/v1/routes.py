from api import common

@app.route("/hello2", methods=['GET', 'POST'])
def hello2():

    data = {
        'status' : 'ok from v1 api routes',
    }

    return jsonify(data)


# common routes




@app.route("/hello1", methods=['GET', 'POST'])
def hello1():

    data = {
        'status' : 'ok from common api',
    }

    return jsonify(data)


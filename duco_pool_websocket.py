from flask import Flask

app = Flask(__name__)


PASSWORD = "123"


@app.route("/api/v2/duco/pools")
def pools():
    pools = DucoPoolList.query.all()

    poolList = []
    for pool in pools:
        poolList.append({'name': pool.name, 'ip': pool.ip, 'port': pool.port, 'status': (pool.status if pool.status != None else False)})

    return jsonify({'result': poolList})




@app.route("/api/v2/duco/pool/update")
def pool_add():
    if 'password' not in request.args:
        print("Error: No Data Provided, Location 2")
        return (jsonify({"error": "No data Provided"}))
    elif 'name' not in request.args:
        print("Error: No Data Provided, Location 2")
        return (jsonify({"error": "No data Provided"}))
    elif 'status' not in request.args:
        print("Error: No Data Provided, Location 2")
        return (jsonify({"error": "No data Provided"}))
    else:
        password = request.args.get('password')
        name = request.args.get('name')
        status = request.args.get('status')

    pools = DucoPoolList.query.filter_by(name=name).first()

    pools.status = status

    if 'ip' in request.args:
        pools.ip = request.args.get('ip')
    if 'port' in request.args:
        pools.port = request.args.get('port')


    if password == PASSWORD:
    db.session.commit()


    return jsonify({'result': True})


# call the 'run' method
app.run(port=80, host=0.0.0.0)

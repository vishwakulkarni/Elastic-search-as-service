import os
from flask import Flask, jsonify, make_response, request

app = Flask(__name__)

log = app.logger

# Service plans
plan_one = {
    "id": "plan_one",
    "name": "plan_one",
    "description": "Simple free plan",
    "free": True
}

# Services
my_service = {
    'id': 'example_service',
    'name': 'example_service',
    'description': 'Simple service example',
    'bindable': True,
    'plans': [plan_one]
}

my_services = {"services": [my_service]}


@app.route('/v2/catalog')
def catalog():
    return jsonify(my_services)


@app.route('/v2/service_instances/<instance_id>', methods=['PUT', 'DELETE',
           'PATCH'])
def service_instances(instance_id):
    if request.method == 'PUT':
        return make_response(jsonify({}), 201)
    else:
        return jsonify({})


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('VCAP_APP_PORT', '5000')))

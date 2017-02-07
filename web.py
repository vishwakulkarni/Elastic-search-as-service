import os
from flask import Flask, jsonify, make_response, request
from functools import wraps

app = Flask(__name__)

log = app.logger

X_BROKER_API_MAJOR_VERSION = 2
X_BROKER_API_MINOR_VERSION = 10
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

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

def api_version_is_valid(api_version):
    version_data = api_version.split('.')
    result = True
    if (float(version_data[0]) < X_BROKER_API_MAJOR_VERSION or
       (float(version_data[0]) == X_BROKER_API_MAJOR_VERSION and
       float(version_data[1]) < X_BROKER_API_MINOR_VERSION)):
                result = False
    return result


def requires_api_version(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        api_version = request.headers.get('X-Broker-Api-Version')
        if (not api_version or not (api_version_is_valid(api_version))):
            abort(412)
        return f(*args, **kwargs)
    return decorated


@app.errorhandler(412)
def version_mismatch(error):
    return 'Version mismatch. Expected: {}: {}.{}'.format(
        X_BROKER_API_VERSION_NAME,
        X_BROKER_API_MAJOR_VERSION,
        X_BROKER_API_MINOR_VERSION), 412

@app.route('/v2/catalog')
@requires_api_version
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

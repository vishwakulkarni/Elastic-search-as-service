import os
from flask import Flask, jsonify

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


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(os.getenv('VCAP_APP_PORT', '5000')))

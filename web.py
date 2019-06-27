import os
from flask import Flask, jsonify, make_response, request
from functools import wraps
import json
import ssh_connection
import requests
import string,random

app = Flask(__name__)

log = app.logger

X_BROKER_API_MAJOR_VERSION = 2
X_BROKER_API_MINOR_VERSION = 10
X_BROKER_API_VERSION_NAME = 'X-Broker-Api-Version'

schemas = {
    "service_binding":{},
    "service_instance": {
        "create": {
            "parameters": {
                "$schema": "http://json-schema.org/draft-06/schema#",
                "title": "createServiceInstance",
                "type": "object",
                "additionalProperties": "false",
                "properties": {
                    "volume_id": {
                        "type": "string",
                        "description": "Id of the volume from which new vm must be created. (Not allowed with backup_name)"
                    },
                    "backup_name": {
                        "type": "string",
                        "pattern": "^[a-zA-Z0-9]+$",
                        "description": "Name of the snapshot from which new vm must be created."
                    },
                    "public_access_required": {
                        "type": [
                            "boolean",
                            "string"
                        ],
                        "description": "Specify whether the service instance should be publically accessible."
                    },
                    "ports": {
                        "type": "string",
                        "pattern": "^[ ]*[1-9][0-9]{0,4}([ ]*-[ ]*[1-9][0-9]{0,4})?([ ]*,[ ]*[1-9][0-9]{0,4}([ ]*-[ ]*[1-9][0-9]{0,4})?)*[ ]*$",
                        "description": "Comma seperated list of ports which are to be opened on the vm. Ex 3000, 4000-4010"
                    },
                    "linked_services": {
                        "type": "string",
                        "description": "Comma separated list of service instance names to which the vm needs connectivity. (Not allowed for vms with public access)"
                    }
                },
                "dependencies": {
                    "volume_id": {
                        "not": {
                            "required": [
                                "backup_name"
                            ]
                        }
                    },
                    "public_access_required": {
                        "oneOf": [{
                                "properties": {
                                    "public_access_required": {
                                        "enum": [
                                            "true"
                                        ]
                                    }
                                },
                                "not": {
                                    "required": [
                                        "linked_services"
                                    ]
                                }
                            },
                            {
                                "properties": {
                                    "public_access_required": {
                                        "not": {
                                            "enum": [
                                                "true"
                                            ]
                                        }
                                    }
                                }
                            }
                        ]
                    }
                }
            }
        },
        "update": {
            "parameters": {
                "$schema": "http://json-schema.org/draft-06/schema#",
                "title": "updateServiceInstance",
                "type": "object",
                "additionalProperties": "false",
                "properties": {
                    "backup_name": {
                        "type": "string",
                        "pattern": "^[a-zA-Z0-9]+$",
                        "description": "Name of the snapshot to which the vm must be restored."
                    },
                    "ports": {
                        "type": "string",
                        "pattern": "^[ ]*[1-9][0-9]{0,4}([ ]*-[ ]*[1-9][0-9]{0,4})?([ ]*,[ ]*[1-9][0-9]{0,4}([ ]*-[ ]*[1-9][0-9]{0,4})?)*[ ]*$",
                        "description": "Comma separated list of ports which are to be opened on the vm. Ex 3000, 4000-4010"
                    },
                    "linked_services": {
                        "type": "string",
                        "description": "Comma separated list of service instance names to which the vm needs connectivity. (Not allowed for vms with public access)"
                    }
                }
            }
        }
    }
}

# Service free plans
basic_one = {
    "id": "basic_small_plan",
    "name": "Single_Node-small",
    "description": "SingeNode-small plan is a free plan for local development",
    "free": True,
    "metadata": {
        "bullets": [
            "Single Node",
            "4 GB storage",
            "Highly Available"
        ]
    },
    'schemas':schemas
}

basic_two = {
    "id": "basic_large_plan",
    "name": "Single_Node-large",
    "description": "SingleNode-large plan is a free plan for local testing",
    "free": True,
    "metadata": {
        "bullets": [
            "Single Node",
            "6 GB storage",
            "Highly Available"
        ]
    }
}

# Services
elastic_service = {
    'id': 'elastic-search',
    'name': 'elastic-search',
    'description': 'elastic-search service to create and manage elastic cluster',
    'bindable': True,
    'plans': [basic_one, basic_two]
}

service_instances = []

service_bindings = []

application_ids = []

elastic_services = {"services": [elastic_service]}

docker = []

docker.append("http://34.239.98.76:9201")
docker.append("http://34.239.98.76:9202")
docker.append("http://34.239.98.76:9205")
docker.append("http://34.239.98.76:9206")

password_management = []

password_management.append("changeme")
password_management.append("changeme")
password_management.append("changeme")
password_management.append("changeme")


docker_assignment = {
    0: "Available",
    1: "Available",
    4: "Available",
    3: "Available",
}


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    print(username, password)
    if not (username == 'alex' and password == 'bob'):
        log.warning('Authentication failed')
    return username == 'alex' and password == 'bob'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response('Could not verify your access level for that URL.\n'
                    'You have to login with proper credentials', 401,
                    {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


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
    print(error)
    return 'Version mismatch. Expected: {}: {}.{}'.format(
        X_BROKER_API_VERSION_NAME,
        X_BROKER_API_MAJOR_VERSION,
        X_BROKER_API_MINOR_VERSION), 412


@app.route('/v2/catalog')
@requires_auth
@requires_api_version
def catalog():
    return jsonify(elastic_services)


@app.route('/v2/service_instances/<instance_id>', methods=['PUT', 'DELETE'])
def service_instances2(instance_id):
    if request.method == 'PUT':
        memory = 4
        data = request.data
        print(data)
        response_data = json.loads(data.decode('utf-8'))
        print(response_data["plan_id"])
        if response_data["plan_id"] == "basic_small_plan":
            memory = 4
        if response_data["plan_id"] == "basic_large_plan":
            memory = 6
        if len(service_instances) > 3:
            return jsonify({"error": "service instace maxed out"}, 404)
        print("service instance got created ", instance_id)
        service_instances.append(instance_id)
        print("sevice instances are : ", service_instances)
        for key, value in sorted(docker_assignment.items()):
            if str(value) == "Available":
                docker_assignment[key] = instance_id
                createElasticSearchInstance(key + 9200 + 1, memory)
                break;
        print("docker assignment are :-")
        for key, value in sorted(docker_assignment.items()):
            print(key, "-->", value)
        if request.method == 'PUT':
            return make_response(jsonify({}), 201)
        else:
            return jsonify({})
    if request.method == 'DELETE':
        for key, value in sorted(docker_assignment.items()):
            if value == instance_id:
                docker_assignment[key] = "Available"
                password_management[key] = "changeme"
                deleteElasticSearchInstance(key + 9200 + 1)
        print("service instances got deleted", instance_id)
        print("sevice instances are : ", service_instances)
        service_instances.remove(instance_id)
        for key, value in sorted(docker_assignment.items()):
            print(key, "-->", value)
        print(service_instances)
        if request.method == 'PUT':
            return make_response(jsonify({}), 201)
        else:
            return jsonify({})


@app.route('/')
def Initial():
    return "well come to elastic search service broker."


@app.route('/v2/service_instances/<instance_id>/service_bindings/<binding_id>', methods=['POST', 'PUT', 'DELETE'])
def service_bindings(instance_id, binding_id):
    if request.method == "DELETE":
        return make_response(jsonify({}))
    print("service bindings done for service instance", instance_id, "with application id", binding_id)
    response_data = json.loads(request.data.decode("utf-8"))
    found = -1
    print("printing response data", response_data)
    for key, value in sorted(docker_assignment.items()):
        print(key, "-->", value)
        if str(value) == instance_id:
            found = key
    print(docker[found], found)
    print(docker_assignment)
    print(service_instances)
    if password_management[found] == "changeme":
        password_management[found] = change_password(found+1+9200)
    print("new password is ",password_management[found])
    getInfo = requests.get("http://elastic:{}@34.239.98.76:{}/".format(password_management[found],found + 1 + 9200))
    clusterName = getInfo.json()["cluster_name"]
    credentials = {
        "name": clusterName,
        "username": "elastic",
        "password": password_management[found],
        "url": docker[found]
    }
    return make_response(jsonify({"credentials": credentials}), 201)


def createSecurityGroup(address):
    url = "https://uaa.cf.stagingaws.hanavlab.ondemand.com/oauth/token"
    payload = "response_type=token&client_id=cf&grant_type=password&client_secret=&username=admin&password=admin"
    headers = {
        'content-type': "application/x-www-form-urlencoded",
        'cache-control': "no-cache",
    }
    response = request.request("POST", url, data=payload, headers=headers)
    response_json = json.loads(response.text)
    accesstoken = response_json["access_token"]
    print(accesstoken)
    url = "https://api.cf.stagingaws.hanavlab.ondemand.com/v2/security_groups"
    payload = {
        "name": "test_service_group",
        "rules": [
            {
                "protocol": "all",
                "destination": address,
                "ports": "9200,9300,9201,9202,9301,9302",
                "log": "true",
                "description": "This rule allows access to Elastic service instance"
            }
        ]
    }
    print(payload)
    headers = {
        'authorization': "bearer "+ accesstoken,
        'content-type': "application/json",
        'cache-control': "no-cache"
    }
    response = request.request("POST", url, data=payload, headers=headers)
    print(response.text)


def createElasticSearchInstance(port, memory):
    if port == 9201:
        ssh_connection.create_instance("alpha", memory, port)
    if port == 9202:
        ssh_connection.create_instance("beta", memory, port)
    if port == 9203:
        ssh_connection.create_instance("gamma", memory, port)
    if port == 9204:
        ssh_connection.create_instance("theta", memory, port)


def deleteElasticSearchInstance(port):
    print("trying to delete with port ", port)
    if port == 9201:
        ssh_connection.delete_instance("alpha")
    if port == 9202:
        ssh_connection.delete_instance("beta")
    if port == 9203:
        ssh_connection.delete_instance("gamma")
    if port == 9204:
        ssh_connection.delete_instance("theta")


def change_password(port):
    url = "http://elastic:changeme@34.239.98.76:{}/_xpack/security/user/elastic/_password".format(port)
    securePassword = ''.join(random.choice(string.ascii_lowercase + string.digits) for _ in range(8))
    passwordChange = {
        "password": securePassword
    }
    headers = {
        "Content-Type": "application/json"
    }
    result = requests.post(url,json.dumps(passwordChange), headers=headers)
    print(result.status_code,result.text)
    return securePassword


if __name__ == "__main__":
    # app.run(host='10.207.116.32', port="33")
    # app.run(host='0.0.0.0', port="33")
    # app.run(host='0.0.0.0', port="8080")
    app.run(host='0.0.0.0', port=int(os.getenv('VCAP_APP_PORT', '5000')))

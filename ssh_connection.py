import paramiko

cmd="sudo docker"
def create_instance(volume,memory,port):
    pubKey = paramiko.RSAKey.from_private_key_file("vishwa_aws.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting")
    client.connect(hostname="34.239.98.76", username="ubuntu", pkey=pubKey)
    print("connected")
    elasticClusterName = "elasticsearch_{}".format(volume)
    createVolumeCommand = "{} volume create --name {}".format(cmd,volume)
    createContainerCommand = "{} run  -d -p {}:9200 -p {}:9300 -e \"xpack.security.enabled=false\"  -m {}g --name {} -v {}:/usr/share/elasticsearch/data -e \"discovery.type=single-node\" docker.elastic.co/elasticsearch/elasticsearch:5.5.3".format(cmd,port,port+100,memory,elasticClusterName,volume)

    stdin, stdout, stderr = client.exec_command(createVolumeCommand)
    print(stdout.read())
    print("error for volume ",stderr.read())
    stdin, stdout, stderr = client.exec_command(createContainerCommand)
    print(stdout.read())
    print("error for creating container ", stderr.read())
    client.close()
    return 1

def delete_instance(volume):
    pubKey = paramiko.RSAKey.from_private_key_file("vishwa_aws.pem")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print("connecting")
    client.connect(hostname="34.239.98.76", username="ubuntu", pkey=pubKey)
    print("connected")
    elasticContainerName = "elasticsearch_{}".format(volume)
    stopContainerCommand = "{} container stop {}".format(cmd,elasticContainerName)
    removeContainerCommand = "{} container rm {}".format(cmd,elasticContainerName)
    deleteVolumeCommand = "{} volume rm {}".format(cmd,volume)
    print("stopping container")
    stdin, stdout, stderr = client.exec_command(stopContainerCommand)
    print(stdout.read())
    print("error for stopping container ", stderr.read())
    print("removing container")
    stdin, stdout, stderr = client.exec_command(removeContainerCommand)
    print(stdout.read())
    print("error for removing container ", stderr.read())
    print("removing volume")
    stdin, stdout, stderr = client.exec_command(deleteVolumeCommand)
    print(stdout.read())
    print("error for deleting volume ", stderr.read())
    client.close()
    return 1
import sys
import docker

image = "wappalyzer/cli"

client = docker.from_env()
client.containers.run(image,  sys.argv[1], True)
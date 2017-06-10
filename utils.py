import hmac
import os
import configparser
import json
import subprocess
from hashlib import sha1


## Useful constants

DOCKER_IMAGE_TAG = "build_bot"
# Thanks to https://github.com/carlos-jenkins/python-github-webhooks/blob/master/webhooks.py
# https://developer.github.com/webhooks/securing/
def verify_signature(header_signature, raw_data, secret):
    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return False
    # HMAC requires the key to be bytes, pass raw request data
    mac = hmac.new(secret, raw_data, sha1)
    # Use compare_digest to avoid timing attacks
    return hmac.compare_digest(str(mac.hexdigest()), str(signature))


def clone_repo(clone_url):
    print("Cloning repo " + clone_url)
    os.system("git -C repos/ clone {} ".format(clone_url))

# TODO : Refactor lose functions to a wrapper class


def check_activity(repo_name):
    target_folder = os.path.join("repos/", repo_name)
    if os.path.exists(target_folder):
        activity_file = os.path.join(target_folder, "activity/activity.info")
        return activity_file
    else:
        return None


def read_activity(activity_file):
    parser = configparser.ConfigParser()
    parser.read(activity_file)
    return parser


def get_activity_attribute(parser, attribute):
    return parser.get('Activity', attribute)


def convert_to_json_string(parser):
    # Get all attrbutes of acitvity
    attributes = parser.items('Activity')
    # Convert attributes to a JSON string
    return json.dumps(dict(attributes))


def convert_to_json_object(parser):
    return json.loads(convert_to_json_string(parser))

def get_activity_manifest(parser):
    attributes = dict(parser.items('Activity'))
    attributes['bundle_name'] = get_bundle_name(parser)
    return json.loads(json.dumps(attributes))


def build_activity(repo_location):
    os.system("./build_activity.sh {}".format(repo_location))

def invoke_build(repo_location):
     invoke_command = "docker run -v /tmp/test:/activities -v $PWD/bundles:/bundles -it {} {}".format(DOCKER_IMAGE_TAG,repo_location)
     result = subprocess.Popen(invoke_command)

def get_bundle_name(parser):
    activity_name = get_activity_attribute(parser,'name')
    activity_version  = get_activity_attribute(parser,'activity_version')
    return activity_name + "-" + activity_version + ".xo"   
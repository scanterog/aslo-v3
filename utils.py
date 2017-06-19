import hmac
import os
import configparser
import json
import subprocess
from hashlib import sha1
import shutil

## Useful constants
DOWNLOAD_LOCATION = "/tmp/activities/"
DOCKER_IMAGE_TAG = "build_bot"
BUNDLE_LOCATION = "/opt/bundles/"

# Thanks to https://github.com/carlos-jenkins/python-github-webhooks/blob/master/webhooks.py
# https://developer.github.com/webhooks/securing/
def verify_signature(header_signature, raw_data, secret):
    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
        return False
    # HMAC requires the key to be bytes, pass raw request data
    # Hmac in Python 3 fails if we don't convert secret to bytes
    secret = str.encode(secret)
    mac = hmac.new(secret, raw_data, sha1)
    # Use compare_digest to avoid timing attacks
    return hmac.compare_digest(str(mac.hexdigest()), str(signature))


def get_target_location(repo_name):
    return os.path.join(DOWNLOAD_LOCATION,repo_name)

def clean_repo(repo_name):
    print("Cleaning up " + repo_name )
    shutil.rmtree(get_target_location(repo_name),ignore_errors=True)

def clone_repo(clone_url):
    print("Cloning repo " + clone_url)
    os.system("git -C {} clone {} ".format(DOWNLOAD_LOCATION,clone_url))

# TODO : Refactor lose functions to a wrapper class


def check_activity(repo_name):
    target_folder = get_target_location(repo_name)
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

def invoke_build(repo_name):
     repo_location = get_target_location(repo_name)
     # This command is condensed with lots of parameters, many man hours were dedicated for it :D
     docker_invoke_command = "docker run -e LOCAL_USER_ID=`id -u $USER` -v {}:/activities -v {}:/bundles -it {} {}".format(DOWNLOAD_LOCATION,BUNDLE_LOCATION,DOCKER_IMAGE_TAG,repo_name)
     print("Invoking Docker with ...")
     print(docker_invoke_command)
     res = os.system(docker_invoke_command)
     print(res)
     return res

def get_bundle_name(parser):
    activity_name = get_activity_attribute(parser,'name')
    activity_version  = get_activity_attribute(parser,'activity_version')
    return activity_name + "-" + activity_version + ".xo"  

def get_bundle_path(bundle_name):
    return os.path.join(BUNDLE_LOCATION,bundle_name)

def verify_bundle(bundle_name):
    bundle_path = get_bundle_path(bundle_name)
    return os.path.exists(bundle_path) and os.path.isfile(bundle_path)
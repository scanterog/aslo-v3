import hmac
import os
import configparser
import json
import subprocess
from hashlib import sha1
import shutil
import requests
import zipfile
## Useful constants
DOWNLOAD_LOCATION = "/tmp/activities/"
DOCKER_IMAGE_TAG = "build_bot"
BUNDLE_LOCATION = "/opt/bundles/"
TEMPORARY_BUNDLES = '/tmp/bundles'

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


def check_bundle(bundle_name):
   xo_file = zipfile.ZipFile(get_bundle_path(bundle_name))
   # Find the acitivity_file and return it
   for filename in xo_file.namelist():
       if 'activity.info' in filename:
           return xo_file.read(filename)
   return None

def get_target_location(repo_name):
    return os.path.join(DOWNLOAD_LOCATION,repo_name)

def clean_repo(repo_name):
    print("Cleaning up " + repo_name )
    shutil.rmtree(get_target_location(repo_name),ignore_errors=True)

def clone_repo(clone_url):
    print("Cloning repo " + clone_url)
    os.system("git -C {} clone {} ".format(DOWNLOAD_LOCATION,clone_url))

# TODO : Refactor lose functions to a wrapper class

# Check if asset is named .xo
def asset_name_check(asset_name):
    return ".xo" in asset_name

def download_asset(download_url,name):
    response = requests.get(download_url, stream=True)
    # Save with every block of 1024 bytes
    with open(TEMPORARY_BUNDLES + "/" + name,"wb") as handle:
        for block in response.iter_content(chunk_size=1024):
            handle.write(block)    
    return

def check_info_file(name):
    xo_file = zipfile.ZipFile(TEMPORARY_BUNDLES+"/"+name)
    return any("activity.info" in filename for filename in xo_file.namelist())


def asset_manifest_check(download_url,bundle_name):
    download_asset(download_url,bundle_name)
    if check_info_file(bundle_name):
      # Check if that bundle already exists then we don't continue
      # Return false if that particular bundle already exists
       if verify_bundle(bundle_name):
           os.remove(TEMPORARY_BUNDLES+"/"+bundle_name)
           return False
       else:
           shutil.move(TEMPORARY_BUNDLES+"/"+bundle_name,BUNDLE_LOCATION)
           return bundle_name
    return False  
   
def check_asset(asset):
    if asset_name_check(asset['name']): 
       return asset_manifest_check(asset['browser_download_url'],asset['name'])
    return False

def check_and_download_assets(assets):
    for asset in assets:
        bundle_name = check_asset(asset)
        if bundle_name:
            return bundle_name
        return False

def check_activity(repo_name):
    target_folder = get_target_location(repo_name)
    if os.path.exists(target_folder):
        activity_file = os.path.join(target_folder, "activity/activity.info")
        return activity_file
    else:
        return None


def read_activity(activity_file,is_string=False):
    parser = configparser.ConfigParser()
    if is_string:
        parser.read_string(activity_file)
    else:
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

import hmac
import os
import ConfigParser
import json
from hashlib import sha1


# Thanks to https://github.com/carlos-jenkins/python-github-webhooks/blob/master/webhooks.py
# https://developer.github.com/webhooks/securing/
def verify_signature(header_signature,raw_data,secret):
    sha_name, signature = header_signature.split('=')
    if sha_name != 'sha1':
       return false
    # HMAC requires the key to be bytes, pass raw request data
    mac = hmac.new(secret,raw_data,sha1)
    # Use compare_digest to avoid timing attacks
    return hmac.compare_digest(str(mac.hexdigest()), str(signature))

def clone_repo(clone_url):
    print "Cloning repo " + clone_url
    os.system("git -C repos/ clone {} ".format(clone_url))

#TODO : Refactor lose functions to a wrapper class

def check_activity(repo_name):
    target_folder = os.path.join("repos/",repo_name)
    if os.path.exists(target_folder):
        activity_file = os.path.join(target_folder,"activity/activity.info")
        return activity_file
    else:
       return None


def read_activity(activity_file):
    parser = ConfigParser.ConfigParser()
    parser.read(activity_file)
    return parser

def get_activity_attribute(parser,attribute):
    return parser.get('Activity',attribute)

def convert_to_json_string(parser):
    # Get all attrbutes of acitvity
    attributes = parser.items('Activity')
    # Convert attributes to a JSON string
    return json.dumps(dict(attributes))

def convert_to_json_object(parser):
    return json.loads(convert_to_json_string(parser))

from flask import Flask, request, abort, render_template
from celery import Celery
import os
from flask_pymongo import PyMongo
from pymongo import MongoClient,DESCENDING
from flask_bootstrap import Bootstrap
import utils
app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['MONGO_DBNAME'] = 'sugar'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/sugar'


## Install BootStrap
Bootstrap(app)

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# Set false for production systems

# Create Mongo instance
# TODO : Secure Mongo to avoid Mongo Ransomware :sweat_smile:
#mongo = PyMongo(app)
client = MongoClient(app.config['MONGO_URI'],connect=False)
app.debug = True
GITHUB_HOOK_SECRET = os.environ.get('GITHUB_HOOK_SECRET')


@app.route('/')
def main():
    return render_template('index.html')

@app.route('/webhook', methods=['POST'])
def handle_payload():
    content = request.get_json(silent=True)
    header_signature = request.headers['X-Hub-Signature']
    if header_signature is None:
        abort(403)
    if not utils.verify_signature(header_signature, request.data, GITHUB_HOOK_SECRET):
        abort(403)

    ## Great if we reach here, it means Webhook was indeed signed by Github and is legit
    # Now we differentiate if it's a hook test or release hook
    
    # We only care about release events for now
    if 'action' and 'repository' and 'release' in content:
         repo_url = content['repository']['clone_url']
         repo_name = content['repository']['name']
         task = build_pipeline.apply_async(args=[repo_url, repo_name])
        
    
   
    return "Authenticated request :D"


@app.route('/test_celery')
def test_celery():
    repo_url = request.args.get('repo_url')
    repo_name = request.args.get('repo_name')
    print("Repo name is " + repo_url)
    task = build_pipeline.apply_async(args=[repo_url, repo_name])
    return "Done"


@celery.task
def build_pipeline(repo_url, repo_name):
    utils.clone_repo(repo_url)
    activity_file = utils.check_activity(repo_name)
    if activity_file is not None:
        #sugar = mongo.db.sugar
        parser = utils.read_activity(activity_file)
        print("Manifest Parsed .. OK")
        #sugar.insert_one(json_object)
        # Check versions before invoking build
        json_object = utils.get_activity_manifest(parser)
        print("JSON Parsed .. OK")
        print(json_object)
        if is_a_new_release(json_object) is False:
            # TODO - Inform Author about Failure
            return "Failure"
        print("Version check .. OK")
        utils.invoke_build(repo_name)
        print("Build DONE .. OK")
        print(json_object)
        utils.clean_repo(repo_name)
        if utils.verify_bundle(json_object['bundle_name']):
           #json_object['xo_build'] = "success"
           update_activity_record(json_object)
           return "Success"
        return "Failure"
    utils.clean_repo(repo_name)
    return "Failure"


def update_activity_record(json_object):
    document = client['sugar']['activities']
    # If a new version exists we inject it as a new document instead of updating old one
    # Since we need to keep record of previous releases
    document.insert_one(json_object)
        
def is_a_new_release(json_object):
    document = client['sugar']['activities']
    # Pymongo really doesn't respect limits. Why :angry:
    # http://api.mongodb.com/python/current/api/pymongo/cursor.html#pymongo.cursor.Cursor.count
    record = document.find({'bundle_id': json_object['bundle_id']}).sort('activity_version',DESCENDING)
    if record.count() == 0:
        return None
    else:
        # Return true if record that exists is less than the version we just build
        # Only compare first result , i.e. most latest one
        # Although version are int only, using float for safety
        print(float(record[0]['activity_version']) < float(json_object['activity_version']))
        return float(record[0]['activity_version']) < float(json_object['activity_version'])

if __name__ == "__main__":
   app.run(host='0.0.0.0')

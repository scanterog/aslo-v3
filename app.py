from flask import Flask,request,abort
from celery import Celery
import os
from IPython import embed
from flask_pymongo import PyMongo
import utils

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'
app.config['MONGO_DBNAME'] = 'sugar'
app.config['MONGO_URI'] = 'mongodb://localhost:27017/sugar'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# Set false for production systems

# Create Mongo instance
#TODO : Secure Mongo to avoid Mongo Ransomware :sweat_smile:
mongo = PyMongo(app)

app.debug = True
GITHUB_HOOK_SECRET = os.environ.get('GITHUB_HOOK_SECRET')

@app.route('/')
def main():
    embed()
    return "Welcome"

@app.route('/webhook',methods=['POST'])
def handle_payload():
    content = request.get_json(silent=True)
    header_signature = request.headers['X-Hub-Signature']
    if header_signature is None:
        abort(403)
    if not utils.verify_signature(header_signature,request.data,GITHUB_HOOK_SECRET):
        abort(403)

    repo_url = content['repository']['clone_url']
    repo_name = content['repository']['name']
    task = clone_repo.apply_async(args=[repo_url,repo_name])
    return "Authenticated request :D"


@app.route('/test_celery')
def test_celery():
    repo_url = request.args.get('repo_url')
    repo_name = request.args.get('repo_name')
    print "Repo name is " + repo_url
    task = process_build.apply_async(args=[repo_url,repo_name])
    return "Done"

@celery.task
def process_build(repo_url,repo_name):
    utils.clone_repo(repo_url)
    acitvity_file = utils.check_activity(repo_name)
    if activity_file not None:
        parsed_json = utils.convert_to_json_object(utils.read_activity(activity_file))
        mongo.db.acitivites.insert(parsed_json)
    return 1
    #check_activity(repo_name)



if __name__ == "__main__":
    app.run(host='0.0.0.0')

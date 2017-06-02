from flask import Flask,request,abort
from celery import Celery
import os
from IPython import embed
import utils

app = Flask(__name__)
app.config['CELERY_BROKER_URL'] = 'redis://localhost:6379/0'
app.config['CELERY_RESULT_BACKEND'] = 'redis://localhost:6379/0'

celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)
# Set false for production systems
app.debug = True
GITHUB_HOOK_SECRET = os.environ.get('GITHUB_HOOK_SECRET')

@app.route('/')
def main():
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
    task = clone_repo.apply_async(args=[repo_url])
    return "Authenticated request :D"


@app.route('/test_celery')
def test_celery():
    repo_url = request.args.get('repo_url')
    print "Repo name is" + repo_url
    task = clone_repo.apply_async(args=[repo_url])
    return "Done"

@celery.task
def clone_repo(repo_url):
    print "Cloning repo " + repo_url
    os.system("git clone {}".format(repo["git_url"]))
    return 15

if __name__ == "__main__":
    app.run(host='0.0.0.0')

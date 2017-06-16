#!/bin/bash
# Builds a sugar activity, accpets repo_name as parameter
set -e
# Temporary bash activation
#source "$HOME/venvs/sugar-dev/bin/activate"
target_repo=$1
#echo $VIRTUAL_ENV
echo "Target repo is $target_repo"
cd "/activities/$target_repo"
echo "Bridge USER ID is $LOCAL_USER_ID"
echo $USER 
echo "Creating Bundle"
python setup.py dist_xo
mkdir -p bundles
#mv dist/*.xo "../../bundles/"
echo "Moving Bundle"
# Assign target repo 
setfacl -R -m u:$LOCAL_USER_ID:rwx "/activities/$target_repo"
cp dist/*.xo /bundles/

echo "Setting up"
#setfacl -R -m u:$LOCAL_USER_ID:rwx $target_repo
#rm -rf "activities/$target_repo"

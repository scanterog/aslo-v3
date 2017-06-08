#!/bin/bash
# Builds a sugar activity, accpets repo_name as parameter
set -e
# Temporary bash activation
#source "$HOME/venvs/sugar-dev/bin/activate"
target_repo=$1
#echo $VIRTUAL_ENV
echo "Target repo is $target_repo"
cd "/activities/$target_repo"

echo "Creating Bundle"
python setup.py dist_xo
#mkdir -p bundles
#mv dist/*.xo "../../bundles/"
echo "Moving Bundle"
mv "dist/*.xo" "/bundles/"

echo "Cleaning up"

rm -rf "activities/$target_repo" 

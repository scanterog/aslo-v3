#!/bin/bash
# Builds a sugar activity, accpets repo_name as parameter
set -e
# Temporary bash activation
source "$HOME/venvs/sugar-dev/bin/activate"
target_repo=$1
echo $VIRTUAL_ENV
echo "Target repo is $target_repo"
cd "repos/$target_repo"
python setup.py dist_xo
mkdir -p bundles
mv dist/*.xo "../../bundles/"
#mv "repos/$target_repo/dist/*.xo" "bundles/"

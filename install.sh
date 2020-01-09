#/bin/bash

# clean up
rm function.zip
rm -rf v-env

# install packages
python3 -m venv v-env
source v-env/bin/activate
pip3 install requests-aws4auth
pip3 install elasticsearch
pip3 install wheel
pip3 install elasticsearch-curator
pip3 install chardet
deactivate

# slim package
cd v-env/lib/python3.6/site-packages
rm -rf ./boto*
rm -rf ./pip*
rm -rf ./*info
find ./ -type f -name '*.pyc' | while read f; do n=$(echo $f | sed 's/__pycache__\///' | sed 's/.cpython-36//'); cp $f $n; done;
find ./ -type d -a -name '__pycache__' -print0 | xargs -0 rm -rf
find ./ -type f -a -name '*.py' -print0 | xargs -0 rm -f
find ./ -iname "*.exe" -exec rm {} \;

# zip packages
zip -r9 ${OLDPWD}/function.zip .
ls

# zip function
cd $OLDPWD
zip -g function.zip lambda_function.py 

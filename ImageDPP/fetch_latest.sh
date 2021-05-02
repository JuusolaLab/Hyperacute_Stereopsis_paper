#
# This script fetches the latest Gonio Imsoft
# from PyPi and Github and creates few README.md pages
#

datenow=$(date)


mkdir wheels
cd wheels
# 
pip download --no-deps gonio-imsoft

# echo "" >> README.md

cat > README.md <<- EOM
# Python wheel package

For all platforms. Fetched from PyPi on $datenow.

## Installation

$(printf '```')
$(printf "pip install $(ls -1  *.whl | tr '\n' ' ' )")
$(printf '```')

### Offline

If installing on a system without internet connection,
you can download 3rd party dependencies on an identitical system
(same OS, same Python version) by

$(printf '```')
$(printf "pip download $(ls -1  *.whl | tr '\n' ' ' )")
$(printf '```')


EOM

cd ..

wheels="$(ls -1  wheels/*.whl | tr '\n' ' ')"
wheels=${wheels//"wheels/"/}

cp source/gonio-imsoft/README.md .





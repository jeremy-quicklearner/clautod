# setup.py is empty because clautod isn't a python library!
# I use dh-virtualenv with the --skip-install option (see debian/rules)
# to manage dependencies on python libraries. requirements.txt is legit
# but setup.py isn't used. Instead, the clautod code is placed outside
# the virtualenv in /usr/share (see debian/install).
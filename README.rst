MDAPI
=====

mdapi (for metadata API) is a simple API aiming at providing as fast as possible
the information contained in the metadata files generated for RPM repositories.
It is currently deployed at:
https://apps.fedoraproject.org/mdapi

You can contribute to mdapi with bug reports or pull requests at:
https://pagure.io/mdapi

Development
-----------
If you wish to set up a
development instance of this project, follow these steps:

* Install virtualenvwrapper

::

    dnf install python-virtualenvwrapper python3-devel openssl-devel

* Get the mkvirtualenv shell function

::

    . /etc/profile.d/virtualenvwrapper.sh

* Create the virtualenv

::

    mkvirtualenv mdapi -p python3

* Install the dependencies

::

    pip install -r requirements.txt

* Download the metadata

::

    ./mdapi-get_repo_md mdapi/default_config.py

* Start the server

::

    ./mdapi-run

* If you need to reactivate the virtual env later, use workon:

::

    workon mdapi


**Note:** This project is python3 only

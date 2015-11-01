MDAPI
=====

mdapi (for metadata API) is a simple API aiming at providing as fast as possible
the information contained in the metadata files generated for RPM repositories.


Development
-----------

If you wish to set-up this project.

* Install virtualenvwrapper

::

    dnf install python-virtualenvwrapper

* Create the virtualenv

::

    mkvirtualenv mdapi

* Install the dependencies

::

    pip install -r requirements.txt

* Download the metadata

::

    mdapi-get_repo_md mdapi/default_config.py

* Start the server

::

    ./mdapi-run


..note: This project is python3 only

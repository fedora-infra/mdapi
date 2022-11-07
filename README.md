# mdapi

A simple and fast API for serving the metadata from the RPM repositories

## Installation

### For development

1. Install [Python 3](https://www.python.org/), [Virtualenv](https://virtualenv.pypa.io/en/latest/) and [Poetry](https://python-poetry.org/) on your Fedora Linux installation.
   ```
   $ sudo dnf install python3 python3-virtualenv poetry
   ```
2. Clone the repository to your local storage and make it your present working directory.
   ```
   $ git clone git@github.com:fedora-infra/mdapi.git
   $ cd mdapi
   ```
3. Set up and activate a virtual environment within the directory of the cloned repository.
   ```
   $ virtualenv venv
   $ source venv/bin/activate
   ```
4. Check the validity of the project configuration and install the project dependencies from the lockfile.
   ```
   $ (venv) poetry check
   $ (venv) poetry install
   ```

### For container image

1. Install [Podman](https://podman.io/) on your Fedora Linux installation.
   ```
   $ sudo dnf install podman
   ```
2. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, following the instructions provided in the **[development installation](#for-development)** section.
   3. The project configuration is modified according to needs in `myconfig.py` file, following the instructions provided in the **[configuration setup](#setting-up-the-configuration)** section.
3. Execute the following command to build the container image.
   ```
   $ (venv) podman build -t "mdapi:$(poetry version -s)" .
   ```

## Usage

### In development

#### Viewing the help message and version

1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, following the instructions provided in the **[development installation](#for-development)** section.
2. Execute the following command to view the help message.
   ```
   $ (venv) mdapi --help
   ```
   Output
   ```
   Usage: mdapi [OPTIONS] COMMAND [ARGS]...
   
     A simple API for serving the metadata from the RPM repositories
   
   Options:
     -c, --conffile PATH  Read configuration from the specified Python file
     --version            Show the version and exit.
     --help               Show this message and exit.
   
   Commands:
     database  Fetch SQLite databases from all active Fedora Linux and EPEL...
     serveapp  Start the API server for querying repository metadata
   ```
3. Execute the following command to view the project version.
   ```
   $ (venv) mdapi --version
   ```
   Output
   ```
   mdapi, version 3.0.0
   ```

#### Testing the project

1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, following the instructions provided in the **[development installation](#for-development)** section.
   3. The storage partition on which [test database directory](https://github.com/fedora-infra/mdapi/blob/develop/tests/__init__.py#L33) is located has at least 1.5 GiB of free space.
2. Execute the following command to run the code quality checks and testcases.
   ```
   $ (venv) tox
   ```

#### Setting up the configuration

1. Ensure that
   1. The project directory is the present working directory.
2. Make a copy of the default configuration on your local storage.
   ```
   $ cp mdapi/confdata/standard.py mdapi/confdata/myconfig.py
   ```
3. Make changes to the copied configuration file to suit the requirements.
   ```
   $ nano confdata/myconfig.py
   ```

#### Fetching the databases

1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, following the instructions provided in the **[development installation](#for-development)** section.
   3. The storage partition on which [database directory](https://github.com/fedora-infra/mdapi/blob/develop/mdapi/confdata/standard.py#L29) is located has at least 6 GiB of free space.
2. Execute the following command to start fetching the database, while referencing to the modified configuration file.
   ```
   $ (venv) mdapi --conffile myconfig.py database
   ```
3. Note that the first run of the database fetching command will take a long time, depending on the internet connection.

#### Serving the application

1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, following the instructions provided in the **[development installation](#for-development)** section.
2. Execute the following command to start serving the application, while referencing to the modified configuration file.
   ```
   $ (venv) mdapi --conffile myconfig.py serveapp
   ```
3. When done with serving the application, press `Ctrl` + `C` to raise a `KeyboardInterrupt` and exit out of the program.

### In container or pod

#### Serving the application

1. Ensure that 
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, following the instructions provided in the **[development installation](#for-development)** section.
   3. The container image is built and available locally.
   4. The databases are downloaded to the [database directory](https://github.com/fedora-infra/mdapi/blob/develop/mdapi/confdata/standard.py#L29), following the instructions provided in the **[database fetching](#fetching-the-databases)** section.
2. Execute the following command to start the serving the application.
   ```
   $ (venv) podman run -v /var/tmp:/var/tmp -p 8080:8080 -ti mdapi:$(poetry version -s)
   ```
   This command assumes that the database directory is `/var/tmp` (which is the [default](https://github.com/fedora-infra/mdapi/blob/develop/mdapi/confdata/standard.py#L29)) and the service port is `8080` (which is the [default](https://github.com/fedora-infra/mdapi/blob/develop/mdapi/confdata/standard.py#L87)).

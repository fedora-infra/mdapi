# mdapi

A simple and fast API for serving the metadata from the RPM repositories

## Installation

### For development

1. Install [Python 3](https://www.python.org/), [Virtualenv](https://virtualenv.pypa.io/en/latest/) and [Poetry](https://python-poetry.org/) on your Fedora Linux installation.
   ```
   $ sudo dnf install python3 python3-virtualenv poetry
   ```
2. Clone the repository to your local storage.
   ```
   $ git clone git@github.com:t0xic0der/mdapi.git
   ```
3. Set up and activate a virtual environment within the directory of the cloned repository.
   ```
   $ virtualenv mdapi/venv
   $ source mdapi/venv/bin/activate
   ```
4. Move into the directory and check the validity of the project configuration.
   ```
   $ (venv) cd mdapi
   $ (venv) poetry check 
   ```
5. Install the project and dependencies from the specified dependency lock file.
   ```
   $ (venv) poetry install
   ```

## Usage

### Viewing the help message and version

1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, from the installation steps.
   ```
   $ source mdapi/venv/bin/activate
   ```
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

### Setting up the configuration

1. Make a copy of the default configuration on your local storage.
   ```
   $ cp mdapi/confdata/standard.py myconfig.py
   ```
2. Make changes to the copied configuration file to suit the requirements.
   ```
   $ nano myconfig.py
   ```

### Fetching the database

1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, from the installation steps.
   ```
   $ source mdapi/venv/bin/activate
   ```
2. Execute the following command to start fetching the database, while referencing to the modified configuration file.
   ```
   $ (venv) mdapi --conffile myconfig.py database
   ```
3. Note that the first run of the database fetching command will take a long time, depending on the internet connection.

### Serving the application
1. Ensure that
   1. The project directory is the present working directory.
   2. The virtual environment with the project is activated, from the installation steps.
   ```
   $ source mdapi/venv/bin/activate
   ```
2. Execute the following command to start serving the application, while referencing to the modified configuration file.
   ```
   $ (venv) mdapi --conffile myconfig.py serveapp
   ```
3. When done with serving the application, press `Ctrl` + `C` to raise a `KeyboardInterrupt` and exit out of the program.

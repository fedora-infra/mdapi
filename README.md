# metasource

```
                                .
                              .o8
ooo. .oo.  .oo.    .ooooo.  .o888oo  .oooo.    .oooo.o  .ooooo.  oooo  oooo  oooo d8b  .ooooo.   .ooooo.
`888P"Y88bP"Y88b  d88' `88b   888   `P  )88b  d88(  "8 d88' `88b `888  `888  `888""8P d88' `"Y8 d88' `88b
 888   888   888  888ooo888   888    .oP"888  `"Y88b.  888   888  888   888   888     888       888ooo888
 888   888   888  888    .o   888 . d8(  888  o.  )88b 888   888  888   888   888     888   .o8 888    .o
o888o o888o o888o `Y8bod8P'   "888" `Y888""8o 8""888P' `Y8bod8P'  `V88V"V8P' d888b    `Y8bod8P' `Y8bod8P'

Performant source for RPM repositories metadata                                                    v0.1.0
```

MetaSource is a performant source for RPM repositories metadata which has an access to the metadata of the different Fedora Linux package repositories and will serve you the most recent information available. It will parse through the "updates-testing" repository before moving onto the likes of "updates" and "releases" repository if no information is found in the previous repository.

Utilize the fast lookup interface to acquaint yourself with the API endpoints and expected outputs. Press `ENTER` after typing the name to execute a lookup in a new window. If you query for a non-existent branch - it will return an **HTTP 400** error. If you query for a non-existent package - it will return an **HTTP 404** error. Please report persistent **HTTP 500** errors to the [Fedora Infrastructure](https://pagure.io/fedora-infrastructure/issues) team.

## Deployment

https://metasource.gridhead.net/

## Development

### Natively

1.  Ensure the most recent version of `go`, `createrepo_c-devel` and `git` installed.
    ```
    $ sudo dnf install go createrepo_c-devel git --setopt=install_weak_deps=False
    ```
2.  Clone the repository contents to your local projects directory.
    ```
    $ git clone https://github.com/gridhead/metasource.git
    ```
3.  Make the cloned repository your present working directory.
    ```
    $ cd metasource
    ```
4.  Build the executable binary using the following command.
    ```
    $ go build -o meta main.go
    ```
5.  View the help contents of the service's command line interface.
    ```
    $ ./meta --help
    ```
    ```
    Usage of ./side:
      -location string
            Set the database location (default "/var/tmp/metasource")
      -loglevel string
            Set the application loglevel (default "info")
    ```
    ```
    $ ./meta
    ```
    ```
    INF Expected either 'database' or 'dispense' subcommand
    ```
6.  Ensure that you have at least 10GiB of storage for RPM repositories metadata.
    ```
    $ df -h
    ```
7.  Download the databases to a temporary directory of your choice.
    ```
    $ ./meta -location /var/tmp/metadata database
    ```
8.  Schedule the database fetching task in a periodically running cronjob.
    ```
    $ cron
    ```
9.  Start the service backend after the database download has finished.
    ```
    $ ./meta -location /var/tmp/metadata dispense
    ```
10. Access the service endpoints using the `curl` command or an internet browser.
    ```
    $ curl -i http://localhost:8080/
    ```
    ```
    HTTP/1.1 200 OK
    Content-Type: text/html
    Vary: Origin
    Date: Tue, 08 Apr 2025 06:29:18 GMT
    Transfer-Encoding: chunked
    ...
    ```
11. Press `Ctrl+C` keyboard combination to shut down the service backend.
    ```
    2025/04/08 06:35:32 "GET http://192.168.0.100/ HTTP/1.1" from 192.168.0.210:48164 - 200 6775B in 115.115µs
    2025/04/08 06:35:35 "GET http://192.168.0.100/branches HTTP/1.1" from 192.168.0.210:48164 - 200 183B in 318.308µs
    2025/04/08 06:35:39 "GET http://192.168.0.100/rawhide/pkg/kernel-devel HTTP/1.1" from 192.168.0.210:48164 - 200 2392B in 3.45733ms
    2025/04/08 06:35:42 "GET http://192.168.0.100/rawhide/srcpkg/python-natsort HTTP/1.1" from 192.168.0.210:48164 - 404 15B in 34.494555ms
    2025/04/08 06:35:45 "GET http://192.168.0.100/rawhide/files/kernel-core HTTP/1.1" from 192.168.0.210:48164 - 200 1038B in 1.038465ms
    2025/04/08 06:35:47 "GET http://192.168.0.100/rawhide/changelog/systemd-networkd HTTP/1.1" from 192.168.0.210:48164 - 200 1924B in 877.515µs
    ^C
    ```
12. Consider contributing to the project with methods that you see feasible.

### Containerized

1.  Ensure the most recent version of [`podman`](https://podman.io/docs/installation) is installed.
    ```
    $ sudo dnf install podman --setopt=install_weak_deps=False
    ```
2.  Clone the repository contents to your local projects directory.
    ```
    $ git clone https://github.com/gridhead/metasource.git
    ```
3.  Make the cloned repository your present working directory.
    ```
    $ cd metasource
    ```
4.  Build the image.
    ```
    $ podman build --security-opt label=disable --tag t0xic0der/metasource:latest .
    ```
5.  Populate the database.
    ```
    $ podman run \
        --rm \
        --volume="metasource_db:/db" \
        --name="metasource" \
        --detach metasource:latest \
        -loglevel info \
        -location /db \
        database
    ```
6.  Execute the container.
    ```
    $ podman run \
        --rm \
        --publish="8080:8080" \
        --volume="metasource_db:/db" \
        --name="metasource" \
        --detach metasource:latest \
        -loglevel info \
        -location /db \
        dispense
    ```

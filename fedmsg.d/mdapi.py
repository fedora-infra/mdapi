""" This is an example mdapi configuration for fedmsg.
By convention, it is normally installed as ``/etc/fedmsg.d/mdapi.py``

For Fedora Infrastructure this file is not needed as we use dynamic
fedmsg endpoints.
"""

import socket
hostname = socket.gethostname().split('.')[0]

config = dict(
    endpoints={
        "mdapi.%s" % hostname: [
            "tcp://127.0.0.1:3005",
        ],
    },
)

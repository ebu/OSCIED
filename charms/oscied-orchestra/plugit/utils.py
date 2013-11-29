import hashlib

from flask import abort
from params import PI_ALLOWED_NETWORKS

import os
import sys

# Decorators
def action(route, template='', methods=['GET']):
    """Decorator to create an action"""
    def real_decorator(function):
        function.pi_api_action = True
        function.pi_api_route = route
        function.pi_api_template = template
        function.pi_api_methods = methods
        return function
    return real_decorator


def only_logged_user():
    """Decorator to specify the action must only be called by logger users"""
    def real_decorator(function):
        function.pi_api_only_logged_user = True
        return function
    return real_decorator


def only_member_user():
    """Decorator to specify the action must only be called by users members of the project"""
    def real_decorator(function):
        function.pi_api_only_member_user = True
        return function
    return real_decorator


def only_admin_user():
    """Decorator to specify the action must only be called by admin users of the project"""
    def real_decorator(function):
        function.pi_api_only_admin_user = True
        return function
    return real_decorator


def only_orga_member_user():
    """Decorator to specify the action must only be called by users members of the organization"""
    def real_decorator(function):
        function.pi_api_only_orga_member_user = True
        return function
    return real_decorator


def only_orga_admin_user():
    """Decorator to specify the action must only be called by admin users of the organization"""
    def real_decorator(function):
        function.pi_api_only_orga_admin_user = True
        return function
    return real_decorator


def cache(time=0, byUser=None):
    """Decorator to specify the number of seconds the result should be cached, and if cache can be shared between users"""
    def real_decorator(function):
        function.pi_api_cache_time = time
        function.pi_api_cache_by_user = byUser
        return function
    return real_decorator


def user_info(props):
    """Decorator to specify a list of properties requested about the current user"""
    def real_decorator(function):
        function.pi_api_user_info = props
        return function
    return real_decorator


def json_only():
    """Decorator to specify the action return json that should be send directly to the browser."""
    def real_decorator(function):
        function.pi_api_json_only = True
        return function
    return real_decorator


def no_template():
    """Decorator to specify the action return template that should be send directly to the browser."""
    def real_decorator(function):
        function.pi_api_no_template = True
        return function
    return real_decorator

# Utils


def md5Checksum(filePath):
    """Compute the MD5 sum of a file"""
    with open(filePath, 'rb') as fh:
        m = hashlib.md5()
        while True:
            data = fh.read(8192)
            if not data:
                break
            m.update(data)
        return m.hexdigest()


def add_unique_postfix(fn):
    """__source__ = 'http://code.activestate.com/recipes/577200-make-unique-file-name/'"""
    if not os.path.exists(fn):
        return fn

    path, name = os.path.split(fn)
    name, ext = os.path.splitext(name)

    make_fn = lambda i: os.path.join(path, '%s(%d)%s' % (name, i, ext))

    for i in xrange(2, sys.maxint):
        uni_fn = make_fn(i)
        if not os.path.exists(uni_fn):
            return uni_fn

    return None


# Class

class PlugItRedirect():
    """Object to perform a redirection"""
    def __init__(self, url, no_prefix=False):
        self.url = url
        self.no_prefix = no_prefix


class PlugItSendFile():
    """Object to send a file to the client browser"""
    """Use the flask function send_file to send the file to the PlugIt client"""
    def __init__(self, filename, mimetype, as_attachment=False, attachment_filename=''):
        self.mimetype = mimetype
        self.filename = filename
        self.as_attachment = as_attachment
        self.attachment_filename = attachment_filename


def addressInNetwork(ip, net):
    "Is an address in a network"
    #http://stackoverflow.com/questions/819355/how-can-i-check-if-an-ip-is-in-a-network-in-python
    import socket
    import struct
    ipaddr = struct.unpack('=L', socket.inet_aton(ip))[0]
    netaddr, bits = net.split('/')
    if int(bits) == 0:
        return True
    netmask = struct.unpack('=L', socket.inet_aton(netaddr))[0] & ((2L << int(bits)-1) - 1)
    return ipaddr & netmask == netmask


def check_ip(request):
    for net in PI_ALLOWED_NETWORKS:
        if addressInNetwork(request.remote_addr, net):
            return True
    # Ip not found
    abort(404)
    return False

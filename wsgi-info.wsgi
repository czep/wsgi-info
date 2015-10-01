"""
    wsgi-info.wsgi

    Author: Scott Czepiel <czep.net>

    Output diagnostic information about a mod_wsgi request environment
    in the style of php's phpinfo() function.

    To install, place the file in a suitable location for wsgi scripts.
    Typically, this would be the parent folder of DOCUMENT_ROOT.  Here,
    I assume /var/www/wsgi-scripts:

    Include the following in httpd.conf:
    WSGIScriptAlias /wsgi-info /var/www/wsgi-scripts/wsgi-info.wsgi

    <Directory /var/www/wsgi-scripts>
        Require all granted
    </Directory>

    Also be sure to read about the WSGIDaemonProcess and WSGIProcessGroup
    directives for deploying wsgi scripts in daemon mode.

    Although primarily intended to be deployed as a mod_wsgi application,
    this script can also be run from the command line:
    $ python wsgi-info.wsgi
"""

import sys
import os
import platform
import datetime
from cgi import escape

html_head = """<!DOCTYPE html>
<html>
<head>
<title>WSGI Info</title>
<meta name="robots" content="noindex,nofollow,noarchive">
<style type="text/css">
body {background-color: #ffffff; color: #000000;}
body, td, th, h1, h2 {font-family: sans-serif;}
pre {margin: 0px; font-family: monospace;}
a:link {color: #000099; text-decoration: none; background-color: #ffffff;}
a:hover {text-decoration: underline;}
table {border-collapse: collapse;}
.center {text-align: center;}
.center table { margin-left: auto; margin-right: auto; text-align: left;}
.center th { text-align: center !important; }
td, th { border: 1px solid #000000; font-size: 75%; vertical-align: baseline;}
h1 {font-size: 150%;}
h2 {font-size: 125%;}
.p {text-align: left;}
.e {background-color: #ccccff; font-weight: bold; color: #000000;}
.h {background-color: #9999cc; font-weight: bold; color: #000000;}
.v {background-color: #cccccc; color: #000000;}
.vr {background-color: #cccccc; text-align: right; color: #000000;}
img {float: right; border: 0px;}
hr {width: 600px; background-color: #cccccc; border: 0px; height: 1px; color: #000000;}
</style>
</head>
<body><div class="center">"""

html_foot = """</body>
</html>
"""

# hard-code the list of attributes/methods to call for each module
params = {}
params['sys'] = ['api_version', 'argv', 'byteorder', 'builtin_module_names', 'copyright', 
    'dont_write_bytecode', 'exec_prefix', 'executable', 'float_info.epsilon', 'float_info.dig', 
    'float_info.mant_dig', 'float_info.max', 'float_info.max_exp', 'float_info.max_10_exp', 
    'float_info.min', 'float_info.min_exp', 'float_info.min_10_exp', 'float_info.radix',
    'float_info.rounds', 'float_repr_style', 'getcheckinterval()', 'getdefaultencoding()', 
    'getdlopenflags()', 'getfilesystemencoding()', 'getrecursionlimit()', 'getwindowsversion()', 
    'hexversion', 'long_info.bits_per_digit', 'long_info.sizeof_digit', 'maxint', 'maxsize', 
    'maxunicode', 'meta_path', 'modules', 'path', 'platform', 'prefix', 'py3kwarning', 
    'subversion', 'tracebacklimit', 'version', 'version_info.major', 'version_info.minor',
    'version_info.micro', 'version_info.releaselevel', 'version_info.serial']

params['os'] = ['getcwd()', 'ctermid()', 'getegid()', 'geteuid()', 'getgid()',
    'getgroups()', 'getpgrp()', 'getpid()', 'getppid()', 'getresuid()',
    'getresgid()', 'getuid()', 'uname()', 'getloadavg()']

params['platform'] = ['architecture()', 'machine()', 'node()', 'platform()',
    'processor()', 'python_build()', 'python_compiler()', 'python_branch()', 
    'python_implementation()', 'python_revision()', 'python_version()', 
    'python_version_tuple()', 'release()', 'system()', 'version()',
    'uname()', 'java_ver()', 'win32_ver()', 'mac_ver()', 'linux_distribution()',
    'libc_ver()']

params['datetime'] = ['datetime.now()', 'datetime.utcnow()']

def start_section(title, html):
    """Layout for start of a new section, if html this will make a new table."""
    if html:
        return ''.join(['<h1>', title, '</h1>\n<table border="0" cellpadding="3" width="600">'])
    else:
        return title + '\n\n'

def table_row(k, v, html):
    """Output a key-value pair as a row in a table."""
    if html:
        return ''.join(['<tr><td class="e">', k, '</td><td class="v">', v, '</td></tr>'])
    else:
        return k + '\n' + v + '\n\n'

def build_output(info, html):
    """Return output based on the dict of lists passed as info."""
    o = []
    if html:
        o.append(html_head)
    else:
        o.append("WSGI Info\n\n")

    # loop through each section in sorted order
    for k in sorted(info):
        section_title = k.split('|')[1]
        o.append(start_section(section_title, html))
        for r in info[k]:
            o.append(table_row(r[0], r[1], html))
        if html:
            o.append('</table>')

    # close main body div
    if html:
        o.append('</div>')

    return ''.join(o)

def wsgi_info(environ, html=True):
    """Gather available data and return a simple web page."""
    info = WSGIInfo(environ)
    info.build()
    return build_output(info.output(), html)


class WSGIInfo():
    """Encapsulate information about this WSGI environment."""
    def __init__(self, environ):
        """Initialize with environ param passed by WSGI."""
        self._environ = environ
        self._data = {}

    def build(self):
        """Populate the _data dict."""
        self.process_params('00|System', 'sys.', params['sys'])
        self.process_params('01|OS', 'os.', params['os'])
        self.process_params('02|Platform', 'platform.', params['platform'])

        # environment variables cannot be hard-coded because some will be
        # implementation/deployment specific, so we add them all here
        for e in sorted(os.environ):
            self.add('03|OS Environment', e, escape(str(os.environ[e])))

        for e in sorted(self._environ):
            self.add('04|WSGI Environment', e, escape(str(self._environ[e])))

        self.process_params('05|Time', 'datetime.', params['datetime'])

    def process_params(self, section, prefix, params):
        """Capture output from a list of module attributes and/or methods."""
        for p in [prefix + p for p in params]:
            try:
                x = eval(p)
            except AttributeError:
                x = ''
            self.add(section, p, escape(str(x)))

    def add(self, section, k, v):
        """Append key-value pair to _data."""
        if section not in self._data:
            self._data[section] = []
        self._data[section].append([k, v])

    def output(self):
        return self._data

    ### end of class WSGIInfo ###


def application(environ, start_response):
    """WSGI application entry point."""
    status = '200 OK'
    output = wsgi_info(environ)
    response_headers = [('Content-type', 'text/html'),
                        ('Content-Length', str(len(output)))]
    start_response(status, response_headers)
    return [output]

if __name__ == '__main__':
    environ = {'SCRIPT_NAME': '__main__'}
    output = wsgi_info(environ, html=False)
    print output

### EOF ###
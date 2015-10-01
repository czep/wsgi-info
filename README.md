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

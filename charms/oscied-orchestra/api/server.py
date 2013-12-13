#!/usr/bin/env python
# -*- coding: utf-8 -*-

#**********************************************************************************************************************#
#              OPEN-SOURCE CLOUD INFRASTRUCTURE FOR ENCODING AND DISTRIBUTION : ORCHESTRA
#
#  Project Manager : Bram Tullemans (tullemans@ebu.ch)
#  Main Developer  : David Fischer (david.fischer.ch@gmail.com)
#  Copyright       : Copyright (c) 2012-2013 EBU. All rights reserved.
#
#**********************************************************************************************************************#
#
# This file is part of EBU Technology & Innovation OSCIED Project.
#
# This project is free software: you can redistribute it and/or modify it under the terms of the EUPL v. 1.1 as provided
# by the European Commission. This project is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY;
# without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the European Union Public License for more details.
#
# You should have received a copy of the EUPL General Public License along with this project.
# If not, see he EUPL licence v1.1 is available in 22 languages:
#     22-07-2013, <https://joinup.ec.europa.eu/software/page/eupl/licence-eupl>
#
# Retrieved from https://github.com/ebu/OSCIED

from __future__ import absolute_import, division, print_function, unicode_literals

import logging, sys
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
from os.path import abspath, dirname, join
from pytoolbox.encoding import configure_unicode
from pytoolbox.logging import setup_logging
from oscied_lib.api import ABOUT, get_test_api_core, OrchestraAPICore
from oscied_lib.config import OrchestraLocalConfig
from oscied_lib.config_test import ORCHESTRA_CONFIG_TEST
from oscied_lib.constants import LOCAL_CONFIG_FILENAME

# ----------------------------------------------------------------------------------------------------------------------

def configure_standalone_mode():
    u"""Return an instance of the flask application after having configured the error handlers."""
    from flask import Flask
    from pytoolbox.flask import json_response
    from oscied_lib.api import api_method_decorator

    app = Flask(__name__)

    @app.errorhandler(400)
    def error_400(value=None):
        return json_response(400, value=value, include_properties=False)

    @app.errorhandler(401)
    def error_401(value=None):
        return json_response(401, value=value, include_properties=False)

    @app.errorhandler(403)
    def error_403(value=None):
        return json_response(403, value=value, include_properties=False)

    @app.errorhandler(404)
    def error_404(value=None):
        return json_response(404, value=value, include_properties=False)

    @app.errorhandler(415)
    def error_415(value=None):
        return json_response(415, value=value, include_properties=False)

    @app.errorhandler(500)
    def error_500(value=None):
        return json_response(500, value=value, include_properties=False)

    @app.errorhandler(501)
    def error_501(value=None):
        return json_response(501, value=value, include_properties=False)

    def ok_200(value, include_properties):
        return json_response(200, value=value, include_properties=include_properties)

    return (app, api_method_decorator, ok_200)

# ----------------------------------------------------------------------------------------------------------------------

def configure_plugit_mode():

    import plugit
    from pytoolbox.flask import json_response
    from server_plugit import api_method_decorator

    def ok_200(value, include_properties):
        return json_response(200, value=value, include_properties=include_properties)

    return (plugit.app, api_method_decorator, ok_200)

# ----------------------------------------------------------------------------------------------------------------------

CONFIG_FILENAME = join(abspath(dirname(__file__)), LOCAL_CONFIG_FILENAME)
CSV_DIRECTORY = join(abspath(dirname(__file__)), u'mock')
HELP_MOCK = u'Mock the MongoDB driver with MongoMock ([WARNING] Still not a perfect mock of the real-one)'

try:
    configure_unicode()
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter, epilog=ABOUT)
    parser.add_argument(u'-m', u'--mock', action=u'store_true', help=HELP_MOCK, default=False)
    args = parser.parse_args()

    if args.mock:
        local_config = ORCHESTRA_CONFIG_TEST
    else:
        local_config = OrchestraLocalConfig.read(CONFIG_FILENAME, inspect_constructor=False)
    setup_logging(console=True, level=local_config.log_level)

    if not local_config.storage_uri():
        logging.warning(u'Shared storage is not set in configuration ... exiting')
        sys.exit(0)

    if not local_config.mongo_admin_connection:
        logging.warning(u'MongoDB is not set in configuration ... mocking')

    if not local_config.rabbit_connection:
        logging.warning(u'RabbitMQ is not set in configuration ... exiting')
        sys.exit(0)

    # Create an instance of the API core
    api_core = get_test_api_core(CSV_DIRECTORY) if args.mock else OrchestraAPICore(local_config)
    is_standalone = api_core.is_standalone

    # Create an instance of the flask application
    #app.config['PROPAGATE_EXCEPTIONS'] = True
    app, api_method_decorator, ok_200 = configure_standalone_mode() if is_standalone else configure_plugit_mode()
    from api_base import *
    from api_environment import *
    from api_media import *
    from api_publisher import *
    from api_transform import *
    from api_user import *
    if not api_core.is_standalone:
        import plugit, views
        plugit.load_actions(views)

    #print(u'Flask URLs Map :\n{0}'.format(app.url_map))

    if __name__ == u'__main__':
        if api_core.is_standalone:
            app.run(host=u'0.0.0.0', debug=api_core.config.verbose)
        else:
            app.run(debug=api_core.config.verbose)

except Exception as error:
    logging.exception(error)
    logging.exception(u'Orchestra ... exiting')
    sys.exit(1)

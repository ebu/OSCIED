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
from pytoolbox.encoding import configure_unicode
from pytoolbox.logging import setup_logging
from pytoolbox.serialization import object2json
from library.oscied_lib.api import ABOUT, get_test_api_core, OrchestraAPICore
from library.oscied_lib.config import OrchestraLocalConfig
from library.oscied_lib.config_test import ORCHESTRA_CONFIG_TEST

# ----------------------------------------------------------------------------------------------------------------------

def configure_standalone_mode():
    u"""Return an instance of the flask application after having configured the error handlers."""
    from flask import Flask
    from pytoolbox.flask import json_response

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

    return (app, ok_200)

# ----------------------------------------------------------------------------------------------------------------------

def configure_plugit_mode():

    import plugit

    def ok_200(value, include_properties):
        # FIXME include_properties not yet handled
        return {u'status': 200, u'value': value}

    return (plugit.app, ok_200)

# ----------------------------------------------------------------------------------------------------------------------

is_mock = True
try:
    configure_unicode()
    config = ORCHESTRA_CONFIG_TEST if is_mock else OrchestraLocalConfig.read(u'local_config.pkl')
    setup_logging(filename=u'orchestra.log', console=True, level=config.log_level)
    logging.info(ABOUT)
    logging.info(u'Configuration : {0}'.format(unicode(object2json(config, True))))

    if not config.storage_uri():
        logging.warning(u'Shared storage is not set in configuration ... exiting')
        sys.exit(0)

    if not config.mongo_admin_connection:
        logging.warning(u'MongoDB is not set in configuration ... mocking')

    if not config.rabbit_connection:
        logging.warning(u'RabbitMQ is not set in configuration ... exiting')
        sys.exit(0)

    # Create an instance of the API core
    orchestra = get_test_api_core() if is_mock else OrchestraAPICore(config)
    orchestra.config.plugit_api_url = u'http://127.0.0.1/'
    logging.info(u'Start REST API')

    # Create an instance of the flask application
    #app.config['PROPAGATE_EXCEPTIONS'] = True
    if orchestra.is_standalone:
        app, ok_200 = configure_standalone_mode()
    else:
        app, ok_200 = configure_plugit_mode()
        # FIXME I MAY PATCH THE ORCHESTRA INSTANCE USER'S METHODS OR ADD THE IF ELSE INTO THE METHODS ...
        # orchestra.requires_auth = lambda *args, **kwargs: None

    if __name__ == u'__main__':
        if orchestra.is_standalone:
            from api_base import *
            from api_environment import *
            from api_media import *
            from api_publisher import *
            from api_transform import *
            from api_user import *
            print(app.url_map)
            app.run(host=u'0.0.0.0', debug=orchestra.config.verbose)
        else:
            import views
            plugit.load_actions(views)
            plugit.app.run(debug=orchestra.config.verbose)

except Exception as error:
    logging.exception(error)
    logging.exception(u'Orchestra ... exiting')
    sys.exit(1)

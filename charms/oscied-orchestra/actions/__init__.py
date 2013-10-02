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

from __future__ import absolute_import

import logging, sys
from library.oscied_lib.api import ABOUT, get_test_api_core, OrchestraAPICore
from library.oscied_lib.config import OrchestraLocalConfig
from library.oscied_lib.config_test import ORCHESTRA_CONFIG_TEST
from library.oscied_lib.pytoolbox.encoding import configure_unicode
from library.oscied_lib.pytoolbox.logging import setup_logging
from library.oscied_lib.pytoolbox.serialization import object2json

# Global variables -----------------------------------------------------------------------------------------------------

# FIXME
global PI_BASE_URL

orchestra = None


# Main method ----------------------------------------------------------------------------------------------------------

def main(flask_app, is_mock):
    global orchestra
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

        orchestra = get_test_api_core() if is_mock else OrchestraAPICore(config)
        logging.info(u'Start REST API')
        #app.config['PROPAGATE_EXCEPTIONS'] = True
        flask_app.run(host=u'0.0.0.0', debug=orchestra.config.verbose)

    except Exception as error:
        logging.exception(error)
        logging.exception(u'Orchestra ... exiting')
        sys.exit(1)


from .base import *
from .environment import *
from .media import *
from .publisher import *
from .transform import *
from .user import *
from .views import *

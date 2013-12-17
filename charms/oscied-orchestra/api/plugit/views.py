
from datetime    import datetime, timedelta
from flask       import request, make_response, send_from_directory, send_file
from flask.views import View
from pytoolbox.serialization import object2json

from utils import check_ip, md5Checksum, PlugItRedirect, PlugItSendFile

from params import PI_META_CACHE


class MetaView(View):
    """The dynamic view (based on the current action) for the /meta method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        objResponse = {}

        # Template information
        objResponse['template_tag'] = ("" if self.action.pi_api_template == "" else
                                       md5Checksum('templates/' + self.action.pi_api_template))

        for attribute in (u'only_logged_user', u'only_member_user', u'only_admin_user',
                          u'only_orga_member_user', u'only_orga_admin_user',  # User restrictions
                          u'cache_time', u'cache_by_user',                    # Cache information
                          u'user_info', u'json_only', 'no_template'):         # Requested user infos + JSON-only
            if hasattr(self.action, u'pi_api_' + attribute):
                objResponse[attribute] = getattr(self.action, u'pi_api_' + attribute)

        # Add the cache headers
        response = make_response(object2json(objResponse, include_properties=False))

        expires = datetime.utcnow() + timedelta(seconds=PI_META_CACHE)
        expires = expires.strftime("%a, %d %b %Y %H:%M:%S GMT")

        response.headers['Expire'] = expires
        response.headers['Cache-Control'] = 'public, max-age=' + str(PI_META_CACHE)

        # Return the final response
        return response


class TemplateView(View):
    """The dynamic view (based on the current action) for the /template method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        # We just return the content of the template
        return send_from_directory('templates/', self.action.pi_api_template)


class ActionView(View):
    """The dynamic view (based on the current action) for the /action method"""

    def __init__(self, action):
        self.action = action

    def dispatch_request(self, *args, **kwargs):

        if not check_ip(request):
            return

        # Call the action
        result = self.action(request, *args, **kwargs)

        # Is it a redirect ?
        if isinstance(result, PlugItRedirect):
            response = make_response("")
            response.headers['EbuIo-PlugIt-Redirect'] = result.url
            if result.no_prefix:
                response.headers['EbuIo-PlugIt-Redirect-NoPrefix'] = 'True'
            return response
        elif isinstance(result, PlugItSendFile):
            response = send_file(result.filename, mimetype=result.mimetype, as_attachment=result.as_attachment, attachment_filename=result.attachment_filename)
            response.headers['EbuIo-PlugIt-ItAFile'] = 'True'
            return response

        return object2json(result, include_properties=False)

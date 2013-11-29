"""Tools to access the PlugIt API"""

import requests

class PlugItAPI(object):
    """Main instance to access plugit api"""

    def __init__(self, url):
        """Create a new PlugItAPI instance, need url as the main endpoint for the API"""
        self.url = url

    def _request(self, uri, params=None, postParams=None, verb='GET'):
        """Execute a request on the plugit api"""
        return getattr(requests, verb.lower())(self.url + uri, params=params, data=postParams, stream=True)

    def get_user(self, userPk):
        """Return an user speficied with userPk"""
        r = self._request('user/' + userPk)
        if r:
            # Set base properties and copy data inside the user
            u = User()
            u.pk = u.id = userPk
            u.__dict__.update(r.json())
            return u
        return None

    def get_orga(self, orgaPk):
        """Return an organization speficied with orgaPk"""
        r = self._request('orga/' + orgaPk)
        if r:
            # Set base properties and copy data inside the orga
            o = Orga()
            o.pk = o.id = orgaPk
            o.__dict__.update(r.json())
            return o
        return None

    def get_project_members(self):
        """Return the list of members in the project"""

        r = self._request('members/')
        if not r:
            return None

        retour = []

        for data in r.json()['members']:

            # Base properties
            u = User()
            u.__dict__.update(data)

            retour.append(u)

        return retour

    def send_mail(self, sender, subject, recipients, message, response_id=None):
        """Send an email using EBUio features. If response_id is set, replies will be send back to the PlugIt server."""

        params = {'sender': sender, 'subject': subject, 'dests': recipients, 'message': message }

        if response_id:
            params['response_id'] = response_id

        return self._request('mail/', postParams=params, verb='POST')


class User(object):
    """Represent an user"""

class Orga(object):
    """Represent an organization"""

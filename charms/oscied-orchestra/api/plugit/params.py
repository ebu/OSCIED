import config

# Global parameters
DEBUG = config.DEBUG

# PlugIt Parameters

# PI_META_CACHE specify the number of seconds meta informations should be cached
if DEBUG:
    PI_META_CACHE = 0  # No cache
else:
    PI_META_CACHE = 5 * 60  # 5 minutes

# Allow the API to be located at another endpoint (to share call with another API)
PI_BASE_URL = config.PI_BASE_URL

# IP allowed to use the PlugIt API.
PI_ALLOWED_NETWORKS = config.PI_ALLOWED_NETWORKS

## Does not edit code bellow !

# API version parameters
PI_API_VERSION = '1'
PI_API_NAME = 'EBUio-PlugIt'

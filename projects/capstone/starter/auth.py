import json
from flask import request, _request_ctx_stack, abort, session, redirect, url_for
from functools import wraps
from jose import jwt
from urllib.request import urlopen


AUTH0_DOMAIN = 'fsnd-jayo.us.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'castagency'

# AuthError Exception
'''
A standardized way to communicate auth failure modes
'''

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


# Auth Header

'''
    Attempts to get the header from the request
    Raises an AuthError if no header is present or header is malformed
    Attempts to split bearer and the token
    Returns the token part of the header
'''
def getResponse(url):
    operUrl = urllib.request.urlopen(url)
    if(operUrl.getcode()==200):
        data = operUrl.read()
        jsonData = json.loads(data)
        print("data received", operUrl.getcode())
    else:
        print("Error receiving data", operUrl.getcode())
    return jsonData
    

def get_token_auth_header():
    auth = request.headers.get('Authorization', None)
    
    if not auth:
        raise AuthError({
            'code': 'authorization_header_missing',
            'description': 'Authorization header is expected.'
        }, 401)

    parts = auth.split()
    if parts[0].lower() != 'bearer':
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must start with "Bearer".'
        }, 401)

    elif len(parts) == 1:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Token not found.'
        }, 401)

    elif len(parts) > 2:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization header must be bearer token.'
        }, 401)

    token = parts[1]
    return token

'''
    Raises an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    Raises an AuthError if the requested permission string is not in
    the payload permissions array return true otherwise
'''


def check_permissions(permission, payload):
    if 'permissions' not in payload:
        raise AuthError({
            'code': 'invalid_claims',
            'description': 'Permissions not included in JWT.'
        }, 400)

    if permission not in payload['permissions']:
        raise AuthError({
            'code': 'unauthorized',
            'description': 'Permission not found.'
        }, 401)
    return True

'''
    Auth0 token with key id (kid). Token is verified using Auth0 /.well-known/jwks.json
    Decodes the payload from the token. Validates the claims
    Returns the decoded payload

    !!NOTE urlopen has a common certificate error described here:
    https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify
    -failed-error-for-http-en-wikipedia-org
'''


def verify_decode_jwt(token):
    # GET THE PUBLIC KEY FROM AUTH0
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())

    # GET THE DATA IN THE HEADER
    unverified_header = jwt.get_unverified_header(token)

    # CHOOSE OUR KEY
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            # USE THE KEY TO VALIDATE THE JWT
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
            }, 400)

'''
    gets token using get_token_auth_header method 
    it should use the verify_decode_jwt method to decode the jwt
    it should use the check_permissions method validate claims and check the
    requested permission
    return the decorator which passes the decoded payload to the decorated
    method
'''


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            try:
                payload = verify_decode_jwt(token)
            except:
                abort(401)

            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)

        return wrapper
    return requires_auth_decorator


def requires_signed_in(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'jwt_token' not in session:
            # Redirect to Login page here
            return redirect(url_for('/'))
        # if 'logged_in' not in session:
        #     # Redirect to Login page here
        #     return redirect(url_for('/'))
        return f(*args, **kwargs)

    return decorated

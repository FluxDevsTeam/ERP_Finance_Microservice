import jwt
import requests
from django.conf import settings
from django.core.exceptions import PermissionDenied
from rest_framework.exceptions import AuthenticationFailed


class IdentityMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        self.identity_url = settings.IDENTITY_MICROSERVICE_URL

    def __call__(self, request):
        # Skip middleware for OPTIONS requests and non-api paths
        if request.method == 'OPTIONS' or not request.path.startswith('/api/'):
            return self.get_response(request)

        try:
            # Extract token from header
            auth_header = request.headers.get('Authorization', '')
            if not auth_header.startswith('Bearer '):
                raise AuthenticationFailed('Invalid authorization header')
            
            token = auth_header.split(' ')[1]
            
            # Verify token with Identity microservice
            response = requests.post(
                f"{self.identity_url}/api/v1/token/verify/",
                json={'token': token}
            )
            
            if response.status_code != 200:
                raise AuthenticationFailed('Invalid or expired token')

            # Get user details and roles
            user_response = requests.get(
                f"{self.identity_url}/api/v1/users/me/",
                headers={'Authorization': f'Bearer {token}'}
            )
            
            if user_response.status_code != 200:
                raise AuthenticationFailed('Failed to fetch user details')

            user_data = user_response.json()
            
            # Attach user info to request
            request.user = type('User', (), {
                'id': user_data['id'],
                'email': user_data['email'],
                'roles': user_data['roles'],
                'is_authenticated': True
            })
            request.tenant_id = user_data['tenant_id']
            request.branch_id = user_data['branch_id']

            # Continue with the request
            response = self.get_response(request)
            return response

        except requests.RequestException:
            raise AuthenticationFailed('Identity service unavailable')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token')
        except Exception as e:
            raise AuthenticationFailed(str(e))
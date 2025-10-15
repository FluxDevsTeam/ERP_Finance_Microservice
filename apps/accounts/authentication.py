from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import get_authorization_header
from django.conf import settings
from rest_framework import exceptions
import jwt

class MicroserviceJWTAuthentication(JWTAuthentication):
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        try:
            validated_token = jwt.decode(
                raw_token,
                settings.JWT_AUTH['SIGNING_KEY'],
                algorithms=['HS256'],
                options={
                    'verify_signature': True,
                    'verify_exp': True,
                    'verify_nbf': True,
                    'verify_iat': True,
                    'verify_aud': True,
                    'verify_iss': True,
                }
            )

            # Verify issuer is our Identity Microservice
            if validated_token.get('iss') != settings.JWT_AUTH['ISSUER']:
                raise jwt.InvalidIssuerError('Invalid token issuer')
            
            # Verify this service is in the audience
            if settings.JWT_AUTH['AUDIENCE'] not in validated_token.get('aud', []):
                raise jwt.InvalidAudienceError('Invalid token audience')

            # Get or create user
            user = self.get_or_create_user(validated_token)
            return user, validated_token

        except jwt.ExpiredSignatureError:
            raise exceptions.AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise exceptions.AuthenticationFailed(str(e))

    def get_or_create_user(self, validated_token):
        """
        Get or create a local user instance based on the token claims.
        """
        from apps.accounts.models import User
        
        try:
            user_id = validated_token[settings.JWT_AUTH['USER_ID_CLAIM']]
            email = validated_token.get('email')
            
            user, created = User.objects.get_or_create(
                id=user_id,
                defaults={
                    'email': email,
                    'is_active': True
                }
            )
            
            # Update user roles from token if present
            if 'roles' in validated_token:
                user.roles = validated_token['roles']
                user.save(update_fields=['roles'])

            return user

        except Exception as e:
            raise exceptions.AuthenticationFailed(f'No user found: {str(e)}')

    def get_header(self, request):
        """
        Extract the header from the request.
        """
        header = get_authorization_header(request).decode('utf-8')
        
        if not header:
            return None
        
        # Check header format
        parts = header.split()
        
        if parts[0].lower() not in ('jwt', 'bearer'):
            return None
        
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. No credentials provided.'
            )

        return header

    def get_raw_token(self, header):
        """
        Extract the raw token from the header.
        """
        parts = header.split()
        
        if len(parts) == 0:
            return None
        
        if len(parts) != 2:
            raise exceptions.AuthenticationFailed(
                'Invalid token header. Token string should not contain spaces.'
            )

        return parts[1]
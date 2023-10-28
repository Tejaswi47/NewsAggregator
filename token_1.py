from itsdangerous import URLSafeTimedSerializer
from key import secret_key
def token(Email,salt):
    serializer= URLSafeTimedSerializer(secret_key)
    return serializer.dumps(Email,salt=salt)
import os

stripe_key = os.environ.get('STRIPE_SECRET_KEY')
public_key = os.environ.get('STRIPE_PUBLIC_KEY')

print(public_key)
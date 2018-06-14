import os
from crypto import NmCrypto

enc = NmCrypto()
S3_BUCKET = "nm-terminator-pdf-parser-input"
S3_KEY = enc.decrypt_file(os.path.abspath("./api/s3_key.enc"))
S3_SECRET = enc.decrypt_file(os.path.abspath("./api/s3_secret.enc"))
S3_LOCATION = 'http://{}.s3.amazonaws.com/'.format(S3_BUCKET)

SECRET_KEY = os.urandom(32)
DEBUG = True
PORT = 5000

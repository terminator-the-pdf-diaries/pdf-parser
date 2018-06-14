import os
import pymysql.cursors
from crypto import NmCrypto

enc = NmCrypto()


def database():
    connection = pymysql.connect(host='pdfterminator-cluster-1.cluster-c5e5ywe0fpem.us-east-2.rds.amazonaws.com',
                                 user='fusion',
                                 password=enc.decrypt_file(
                                     os.path.abspath("./api/db.enc")),
                                 db='PDFDiary',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

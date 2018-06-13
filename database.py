import pymysql.cursors


def database():
    connection = pymysql.connect(host='pdfterminator-cluster-1.cluster-c5e5ywe0fpem.us-east-2.rds.amazonaws.com',
                                 user='fusion',
                                 password='NMwit2018',
                                 db='PDFDiary',
                                 cursorclass=pymysql.cursors.DictCursor)
    return connection

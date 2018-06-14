
from flask import Flask, request, Response
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify
from flask_cors import CORS
from database import database
from s3 import upload_file_to_s3
from config import S3_LOCATION, S3_KEY, S3_SECRET, S3_BUCKET

app = Flask(__name__)
app.config['CORS_HEADERS'] = ['Content-Type']
app.config["S3_BUCKET"] = S3_BUCKET
cors = CORS(app, resources={r"/api": {"origins": "*"}})

api = Api(app)

try:
    cur = database().cursor()
    print("connected")
except ValueError:
    print("Oops! Cannot connect to the database...")


class Rule_Helper:
    _company_id = None

    def __init__(self, id=None):
        self._company_id = id

    def query(self, column, table):
        if (self._company_id is None):
            return """SELECT %s FROM %s""" % (column, table)
        else:
            return """SELECT %s FROM %s WHERE Company_ID = %s""" % (
                column, table, self._company_id)

    def get_company(self):
        sql = self.query("*", "Company")
        cur.execute(sql)
        result = cur.fetchall()
        return result

    def get_format(self):
        sql = self.query(
            "*", "Company_Financial_Statement_Format")
        cur.execute(sql)
        result = cur.fetchone()
        print(result)
        return result

    def get_column_headers(self):
        result = []
        sql = self.query("Column_Header_Text",
                         "Financial_Statement_Column_Header")
        cur.execute(sql)
        data_set = cur.fetchall()
        for row in data_set:
            result.append(row["Column_Header_Text"])
        return result

    def get_excluded_headers(self):
        result = []
        if (self._company_id is None):
            sql = """SELECT Column_Header_Text
            FROM Financial_Statement_Column_Header C
            WHERE C.Discard_Column = True
            """
        else:
            sql = """SELECT Column_Header_Text
            FROM Financial_Statement_Column_Header C
            WHERE C.Discard_Column = True AND C.Company_ID = %s
            """ % (self._company_id)
        cur.execute(sql)
        data_set = cur.fetchall()
        print(data_set)
        for row in data_set:
            result.append(row["Column_Header_Text"])
        return result

    def get_keyword_match(self):
        result = []
        if (self._company_id is None):
            sql = """SELECT Word.Key_Word_Text, IA.IA_Classification_Text
                FROM Key_words_IA_Clasification Rel
                LEFT JOIN Key_words Word ON Word.Key_Word_Code = Rel.Key_Word_Code
                LEFT JOIN IA_Clasification IA ON IA.IA_Classification_Code =  Rel.IA_Classification_Code"""
        else:
            sql = """SELECT Word.Key_Word_Text, IA.IA_Classification_Text
                FROM Key_words_IA_Clasification Rel
                LEFT JOIN Key_words Word ON Word.Key_Word_Code = Rel.Key_Word_Code
                LEFT JOIN IA_Clasification IA ON IA.IA_Classification_Code =  Rel.IA_Classification_Code
                WHERE Rel.Company_ID = %s""" % (self._company_id)

        cur.execute(sql)
        data_set = cur.fetchall()
        for row in data_set:
            _pattern = {
                row["Key_Word_Text"]: row["IA_Classification_Text"]
            }
            result.append(_pattern)
        return result


class Helpers:
    @staticmethod
    def convert_list_to_dic(items):
        result = {}
        for item in items:
            for attr, value in item.items():
                result[attr] = value
        return result


class Rules(Resource):
    def get(self, id=None):
        result = []
        _companies = Rule_Helper().get_company()

        for row in _companies:
            _id = row["Company_ID"]
            _rules = {}
            # Get format, headers and keyword_match
            _format = Rule_Helper(_id).get_format()
            for attr, value in _format.items():
                _rules[attr] = value

            _rules["headers"] = Rule_Helper(_id).get_column_headers()
            _rules["excluded_header"] = Rule_Helper(_id).get_excluded_headers()
            _rules["keyword_match"] = Helpers.convert_list_to_dic(
                Rule_Helper(_id).get_keyword_match())

            _company = {
                row["Company_Name"]: _rules
            }
            result.append(_company)

        return result


class Rule(Resource):

    def get(self, id):
        _format = Rule_Helper(id).get_format()
        _headers = Rule_Helper(id).get_column_headers()
        _excluded_headers = Rule_Helper(id).get_excluded_headers()
        _keyword_match = Helpers.convert_list_to_dic(
            Rule_Helper(id).get_keyword_match())
        result = {
            "format": _format,
            "headers": _headers,
            "excluded_headers": _excluded_headers,
            "keyword_match": _keyword_match
        }
        return result


class Upload(Resource):
    def post(self):
        # file = request.files.get('file')
        file = request.files["files"]
        # HACK: Replace with conver data method
        # Use Tika to parse the PDF
        #parsedPDF = parser.from_buffer(file.read())
        #print('pdf', parsedPDF["content"])

        output = upload_file_to_s3(file, app.config["S3_BUCKET"])
        return str(output)

    def options(self):
        resp = Response()
        resp.headers['Access-Control-Allow-Origin'] = '*'
        resp.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        resp.headers['Access-Control-Allow-Methods'] = 'POST'
        return resp


api.add_resource(Rules, '/api//rules', methods=['GET'])
api.add_resource(Rule, '/api/rules/<id>',
                 methods=['GET', 'POST', 'DELETE', 'PUT'])
api.add_resource(Upload, '/api/upload', methods=['POST', 'OPTIONS'])


if __name__ == '__main__':
    app.run(debug=True)

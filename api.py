
from flask import Flask, request
from flask_restful import Resource, Api
from json import dumps
from flask_jsonpify import jsonify

from database import database

app = Flask(__name__)
api = Api(app)

try:
    cur = database().cursor()
    print("connected")
except ValueError:
    print("Oops! Cannot connect to the database...")


class Rule(Resource):
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
        print(data_set)
        for row in data_set:
            _pattern = {
                row["Key_Word_Text"]: row["IA_Classification_Text"]
            }
            result.append(_pattern)
        return result

    def get(self):
        _format = self.get_format()
        _headers = self.get_column_headers()
        _keyword_match = self.get_keyword_match()
        result = {
            "format": _format,
            "headers": _headers,
            "keyword_match": _keyword_match
        }
        return jsonify(result)


class Rules(Resource):

    def get(self, id=None):
        result = []
        _companies = Rule().get_company()

        for row in _companies:
            _id = row["Company_ID"]
            _rules = {}
            print('here', _id)
            # Get format, headers and keyword_match
            _format = Rule(_id).get_format()
            print('here', _format)
            for attr, value in _format.items():
                _rules[attr] = value

            _rules["headers"] = Rule(_id).get_column_headers()

            _rules["keyword_match"] = Rule(_id).get_keyword_match()

            _company = {
                row["Company_Name"]: _rules
            }
            result.append(_company)

        return jsonify(result)


api.add_resource(Rules, '/rules', methods=['GET'])
api.add_resource(Rule, '/rules/<id>', methods=['GET', 'POST', 'DELETE'])


if __name__ == '__main__':
    app.run(debug=True)

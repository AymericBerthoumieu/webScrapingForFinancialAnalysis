from API.pipeline import pipeline_from_csv, pipeline_direct
from flask_restful import Resource, Api, reqparse
from flask import Flask
import pandas as pd


class Correlation(Resource):

    def get(self):
        parser = reqparse.RequestParser()

        corr_pearson, corr_sign = pipeline_from_csv()

        dict_return = {
            "sign_correlation": corr_sign,
            "pearson_correlation": corr_pearson
        }
        return dict_return, 200


class Correlation_direct(Resource):

    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('ticker', required=True)
        parser.add_argument('influencers', required=True)

        args = parser.parse_args()

        corr_pearson, corr_sign = pipeline_direct(args['ticker'], args['influencers'].split(','))

        dict_return = {
            "sign_correlation": corr_sign,
            "pearson_correlation": corr_pearson
        }
        return dict_return, 200


app = Flask("Sentiment Correlation Scrapper")
api = Api(app)
api.add_resource(Correlation, '/replay')
api.add_resource(Correlation_direct, '/correlation_live')

if __name__ == "__main__":
    app.run()

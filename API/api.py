from API.pipeline import pipeline_from_csv, pipeline_direct
from flask_restful import Resource, Api, reqparse
from flask import Flask


class Correlation(Resource):

    def get(self):

        corr_pearson, corr_sign, posts, levels = pipeline_from_csv()
        levels.index = levels.index.astype(str)
        posts.index = posts.index.astype(str)

        dict_return = {
            "sign_correlation": corr_sign,
            "pearson_correlation": corr_pearson,
            "posts": posts.to_dict(),
            "levels": levels.to_dict()
        }
        return dict_return, 200


class CorrelationDirect(Resource):

    def get(self):
        parser = reqparse.RequestParser()

        parser.add_argument('ticker', required=True)
        parser.add_argument('influencers', required=True)

        args = parser.parse_args()

        corr_pearson, corr_sign, posts, levels = pipeline_direct(args['ticker'], args['influencers'].split(','))
        levels.index = levels.index.astype(str)
        posts.index = posts.index.astype(str)

        dict_return = {
            "sign_correlation": corr_sign,
            "pearson_correlation": corr_pearson,
            "posts": posts.to_dict(),
            "levels": levels.to_dict()
        }
        return dict_return, 200


app = Flask("Sentiment Correlation Scrapper")
api = Api(app)
api.add_resource(Correlation, '/replay')
api.add_resource(CorrelationDirect, '/correlation_live')

if __name__ == "__main__":
    app.run()

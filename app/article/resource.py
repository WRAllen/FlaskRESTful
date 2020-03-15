from flask_restful import Resource, reqparse

from app import db
from app.user.models import User
from app.auth import token_required
from app.system_config import SysConfig
from .models import Article
from .schema import ArticleSchema


parser = reqparse.RequestParser()


class ArticleResource(Resource):
    # 全部请求都验证:get,post,put,delete
    # method_decorators = [authenticate]
    # 只验证字典里面列出的请求类型,下面就是只对get和post进行token认证
    method_decorators = {
        'get': [token_required], "post": [token_required],
        "put": [token_required], "delete": [token_required]
    }

    def get(self, *args, **kwargs):
        parser.add_argument("Page")
        args = parser.parse_args()
        page = int(args["Page"]) if args["Page"] else 1
        print("page", page, type(page))
        pagination = db.session.query(
            Article.ID, Article.Title, Article.Text
        ).paginate(page, per_page=8, error_out=False)
        articles = pagination.items
        article_schema = ArticleSchema(many=True)
        return article_schema.dump(articles)

    def post(self, *args, **kwargs):
        try:
            parser.add_argument("Title")
            parser.add_argument("Text")
            parser.add_argument("UserID")
            args = parser.parse_args()
            new_artile = Article()
            new_artile.Title = args["Title"]
            new_artile.Text = args["Text"]
            new_artile.UserID = args["UserID"]
            db.session.add(new_artile)
            db.session.commit()
            return {"code": 200, "message": "添加成功!"}
        except Exception as e:
            return {"code": 204, "message": "添加失败!"+e}

    def put(self, *args, **kwargs):
        parser.add_argument("ArticleID")
        parser.add_argument("Title")
        parser.add_argument("Text")
        args = parser.parse_args()
        check_article = Article.query.get(args["ArticleID"])
        if not check_article:
            return SysConfig.ReturnCode("ARTICLE_NOT_EXIST")
        check_article.Title = args["Title"]
        check_article.Text = args["Text"]
        try:
            db.session.commit()
            return SysConfig.ReturnCode("CHANGE_SUCCESS")
        except Exception as e:
            db.session.rollback()
            return {"code": 204, "message": f"添加失败!{str(e)}"}

    def delete(self, *args, **kwargs):
        parser.add_argument("ArticleID")
        args = parser.parse_args()
        check_article = Article.query.get(args["ArticleID"])
        if not check_article:
            return SysConfig.ReturnCode("ARTICLE_NOT_EXIST")
        db.session.delete(check_article)
        try:
            db.session.commit()
            return SysConfig.ReturnCode("DELETE_SUCCESS")
        except Exception as e:
            db.session.rollback()
            return {"code": 204, "message": f"删除失败!{str(e)}"}


class ArticleSingleResource(Resource):
    method_decorators = {'get': [token_required]}

    def get(self, *args, **kwargs):
        print("-------进入---------------")
        parser.add_argument("ArticleID")
        args = parser.parse_args()
        print(f"ArticleID:{args['ArticleID']}, type:{type(args['ArticleID'])}")
        article = Article.query.get(args['ArticleID'])
        if not article:
            return SysConfig.ReturnCode("ARTICLE_NOT_EXIST")
        article_schema = ArticleSchema()
        return article_schema.dump(article)
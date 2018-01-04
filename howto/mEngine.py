__author__ = 'unclecode'

# mongoengine pagination
# if params['slug']:
#     self.category = ArticleCategory.objects.get(slug=params['slug'])
#
# if self.category:
#     articles = Article.objects(categories=self.category).order_by(params['order_by']).paginate(page=params['page'], per_page=params['size']).items
# else:
#     articles = Article.objects.all().order_by(params['order_by']).paginate(page=params['page'], per_page=params['size']).items

from django.contrib import admin
from blog.models import Post, Comment, CreditAquisition, Transactions, Wallet, ContentItem


admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(CreditAquisition)
admin.site.register(Transactions)
admin.site.register(Wallet)
admin.site.register(ContentItem)

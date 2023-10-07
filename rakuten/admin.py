from django.contrib import admin

#作成したモデルをインポート
from .models import(
    Categories, Products, Users
)

#管理画面にレジスターする
admin.site.register(
    [Categories, Products, Users]
)
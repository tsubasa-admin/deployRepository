from django.db import models

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser, PermissionsMixin
)
from django.urls import reverse_lazy

#ユーザーのマネージャー
class UserManager(BaseUserManager):
    def create_user(self, username, email, password=None):
        if not email:
            raise ValueError('Enter Email')
        user = self.model(
            username=username,
            email=email
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

#ユーザーのテーブル
class Users(AbstractBaseUser, PermissionsMixin):
    
    #登録された日
    cretate_at = models.DateTimeField('登録日', auto_now_add=True)
    
    #更新された日
    update_at = models.DateTimeField('更新日', auto_now=True)
    
    #ユーザー名
    username = models.CharField(max_length=150)
    
    #メールアドレス
    email = models.EmailField(max_length=255, unique=True)
    
    #登録すればログインできる
    is_active = models.BooleanField(default=True)
    
    #管理画面にログインできる
    is_staff = models.BooleanField(default=False)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = UserManager()

    def get_absolute_url(self):
        return reverse_lazy('rakuten:home')


#商品のカテゴリーのテーブル
class Categories(models.Model):
    
    #登録された日
    cretate_at = models.DateTimeField('登録日', auto_now_add=True)
    
    #更新された日
    update_at = models.DateTimeField('更新日', auto_now=True)
    
    #カテゴリーの名前(冷蔵庫、洗濯機、ベッド)
    name = models.CharField('カテゴリー', max_length=20) 
    
    #カテゴリーのURL(楽天ランキングのURL(冷蔵庫、洗濯機、ベッド))
    url = models.URLField('URL') 
    
    #ユーザーごとのカテゴリーを表示
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE,
    )   
    
    class Meta:
        #テーブル名
        db_table = 'categories'
        
        #strでnameを返す    
    def __str__(self):
        return self.name
    
#商品の種類のテーブル
class Products(models.Model):
    
    #登録された日(スクレイピングでDBに保存した日)
    cretate_at = models.DateTimeField('登録日', auto_now_add=True)
    
    #更新された日(スクレイピングでDBに保存した日)
    update_at = models.DateTimeField('更新日', auto_now=True)
    
    #商品名
    name = models.CharField('商品名', max_length=100) 
    #商品url
    url = models.URLField('商品URL') 
    #店舗名
    store = models.CharField('店舗名', max_length=100) 
    #価格
    price = models.IntegerField('価格') 
    #変動価格
    price_fluctuation = models.IntegerField('変動価格', blank=True) 
    
    #カテゴリーと紐づける(※カテゴリーが削除されると削除される)
    category = models.ForeignKey(
        Categories, on_delete=models.CASCADE,
    )
    
    #ユーザーと紐づける(※ユーザーが削除されると削除される)
    user = models.ForeignKey(
        Users, on_delete=models.CASCADE,
    )      
    
    class Meta:
        #テーブル名
        db_table = 'products'
    
    #strでnameと登録日時を返す    
    def __str__(self):
        return str(self.name)
from django import forms

#作成したmodelをインポート
from .models import (
    Categories, Products, Users
)

from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm

#ユーザーの登録するモデルフォーム
class RegistForm(forms.ModelForm):
    username = forms.CharField(label='名前')
    age = forms.IntegerField(label='年齢', min_value=0)
    email = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())

    class Meta:
        model = Users
        fields = ['username', 'age', 'email', 'password']
    
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user

#ログインをするフォーム
class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス')
    password = forms.CharField(label='パスワード', widget=forms.PasswordInput())


#カテゴリーを登録するモデルフォーム
class CategoryModelForm(forms.ModelForm):
    
    class Meta:
        #モデル
        model = Categories
        #フィールドはすべて
        fields = ('name', 'url')
        
#商品を登録するモデルフォーム
class ProductModelForm(forms.ModelForm):
    
    class Meta:
        #モデル
        model = Products
        #フィールドはすべて
        fields = ('name', 'url', 'store', 'price', 'price_fluctuation', 'category')
    
    #ユーザー事のカテゴリーをformに表示するために初期化
    def __init__(self, *args, **kwargs):
        
            # ユーザーを取得
            user = kwargs.pop('user', None)  
            super().__init__(*args, **kwargs)
            
            # ユーザーごとの処理を追加
            if user:
                # ユーザーに紐づくカテゴリーのみを改めて「category」フィールドに追加
                self.fields['category'].queryset = Categories.objects.filter(user=user)
        
#カテゴリーを更新するモデルフォーム
class CategoryUpdateForm(forms.ModelForm):
    
    class Meta:
        #モデル
        model = Categories
        #フィールドはすべて
        fields = ('name', 'url')
        
#商品を更新するモデルフォームを
class ProductUpdateForm(forms.ModelForm):
    
    class Meta:
        #モデル
        model = Products
        #フィールドはすべて
        fields = ('name', 'url', 'store', 'price', 'price_fluctuation','category')
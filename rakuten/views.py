from django.shortcuts import render
from django.views.generic.edit import (
    FormView, UpdateView, DeleteView, CreateView
)

from django.views.generic import TemplateView, ListView 
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.urls import reverse_lazy

from .import forms
#フォームをインポート
from .models import Categories, Products

from bs4 import BeautifulSoup
import requests
import pandas as pd

#homeのテンプレート
class home_templateView(LoginRequiredMixin, TemplateView):
    template_name = "home.html"
    
    #ユーザー情報をテンプレートに渡す
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        #ログインユーザーと変動価格が０以上の降順で抽出してテンプレートに渡す
        context['object_list'] = Products.objects.filter(price_fluctuation__gte=1, user=self.request.user).order_by('-price_fluctuation')[0:5]
        return context

#ユーザー登録
class RegistUserView(CreateView):
    template_name = 'regist.html'
    form_class = forms.RegistForm    

#ログイン    
class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = forms.UserLoginForm
    
#ログアウト
class UserLogoutView(LogoutView):
    pass

# カテゴリー新規作成
class CategoryFormView(LoginRequiredMixin, FormView):
    template_name = "category_form.html"
    form_class = forms.CategoryModelForm
    success_url = reverse_lazy('rakuten:category_list')
    
    #カテゴリーの新規登録
    def form_valid(self, form):
        if form.is_valid():
            
            # 保存前にログイン中のユーザーをformに入れる
            form.instance.user_id = self.request.user.id # type: ignore
            form.save()  # type: ignore
        return super(CategoryFormView, self).form_valid(form)

#商品情報(個別)に新規登録   
class ProductFormView(LoginRequiredMixin, FormView):
    template_name = "product_form.html"
    form_class = forms.ProductModelForm
    success_url = reverse_lazy('rakuten:product_list')
    
    #商品情報の新規登録(DBに登録)
    def form_valid(self, form):
        if form.is_valid():
            
            # 保存前にログイン中のユーザーをformに入れる
            form.instance.user_id = self.request.user.id # type: ignore
            form.save()  # type: ignore
        return super(ProductFormView, self).form_valid(form) # type: ignore
    
    #ユーザー事のカテゴリーを用事する(forms.pyに渡す)
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        #ユーザー情報を渡す
        kwargs['user'] = self.request.user
        return kwargs
    
#登録したカテゴリーを表示
class CategoryListView(LoginRequiredMixin, ListView):
    template_name = 'category_list.html'
    model = Categories

#カテゴリーの詳細画面
class CategoryDetailView(LoginRequiredMixin, DetailView):
    model = Categories
    template_name = 'detail_category.html'
    success_url = reverse_lazy('rakuten:product_list')
    
    #カテゴリーの詳細画面のpostの場合に処理する
    def post(self, request, *args, **kwargs):

        #IDからカテゴリーのURLを取得
        id = request.POST["id"]
        url = Categories.objects.values_list('url', flat=True).get(pk=id)
        res = requests.get(str(url))
        soup = BeautifulSoup(res.text, 'html.parser')
        soups = soup.find_all('div', attrs={'class':'rnkRanking_upperbox'} )
        data = []

        #商品名、商品url、お店の名前取得し、リストに追加
        for Rankdata in soups:
                Rank_Name = Rankdata.find('div', attrs={'class':'rnkRanking_itemName'} )
                Rank_Name = Rank_Name.text
                Rank_url = Rankdata.find_all('a')[0].get('href')
                shop_name = Rankdata.find('div', attrs={'rnkRanking_shop'} ).text
                ranking_item={
                    'name':Rank_Name,
                    'url':Rank_url,
                    'store':shop_name,
                }
                
                data.append(ranking_item)

        data_price = []

        #価格だけ別BOXのため再度実行
        soups = soup.find_all('div', attrs={'class':'rnk_fixedRightBox'} )    
        for Rankdata in soups:
                Rank_Name = Rankdata.find('div', attrs={'class':'rnk_fixedRightBox'} )
                shop_price = Rankdata.find('div', attrs={'rnkRanking_price'} ).text
                ranking_item={
                    'price':shop_price,
                }
                
                data_price.append(ranking_item)

        #DFに変換し統合
        df1 = pd.DataFrame(data)
        df2 = pd.DataFrame(data_price)
        df = pd.concat([df1, df2], axis=1)

        #Dfをループして一つずつProductsに保存
        for d in df.itertuples():
            
            #不要な文字を削除
            price= d.price.replace('円', '')
            new_price= price.replace(',', '')

            #スクレイピングで取得した商品名とURLとに該当する情報を取得
            qs_filter = Products.objects.filter(name=d.name, url=str(d.url), user=self.request.user).count()
            
            if qs_filter == 0:
                #DBに登録なければそのまま登録
                obj, created = Products.objects.get_or_create(name=d.name, url=d.url, store=d.store, price=new_price, price_fluctuation=0, category_id=id ,user=self.request.user) 

            else:
                #DBに登録があれば商品名とURLでデータ取得
                qs_filter = Products.objects.filter(name=d.name, url=str(d.url), user=self.request.user)

                #<QuerySet>はfor分で一つずつ取り出す。
                for q in qs_filter:
                    
                    #登録されている価格と相違がある場合
                    if q.price != int(new_price):
                        print(q.pk)
                        print(q.price)
                        print(new_price)
                        #Productsの価格変動に登録
                        Products.objects.filter(pk=q.pk).update(price_fluctuation=new_price)
                        
        #商品情報一覧に遷移する際にデータも一緒にtemplateに渡す   
        context = {}
        qs = Products.objects.all()
        context["object_list"] = qs
            
        return render(request, 'product_list.html', context)
    
    
#カテゴリーの更新画面
class CategoryUpdateView(LoginRequiredMixin, UpdateView):
    model = Categories
    template_name = 'update_category.html'
    form_class = forms.CategoryUpdateForm
    success_url = reverse_lazy('rakuten:category_list')
    
#カテゴリーの削除画面
class CategoryDeleteView(LoginRequiredMixin, DeleteView):
    model = Categories
    template_name = 'delete_category.html'
    success_url = reverse_lazy('rakuten:category_list')  

#商品情報リストのテンプレート
class ProductListView(LoginRequiredMixin, ListView):
    model = Products
    template_name = 'product_list.html'
    
    #検索ボタン
    def get_queryset(self):
        query = super().get_queryset()
        product_name = self.request.GET.get('product_name', None)
        if product_name:
            query = query.filter(
                name__contains = product_name
            )
        #昇順、降順
        price_fluctuation = self.request.GET.get('price_fluctuation', 0)
        if price_fluctuation == '1':
            query = query.order_by('price_fluctuation')
        elif price_fluctuation == '2':
            query = query.order_by('-price_fluctuation')
        return query
    
    #検索した文字を表示したままにする
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['product_name'] = self.request.GET.get('product_name', '')
        price_fluctuation = self.request.GET.get('price_fluctuation', 0)
        if price_fluctuation == '1':
            context['ascending'] = True
        elif price_fluctuation == '2':
            context['descending'] = True
        return context
        
#商品の詳細画面
class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Products
    template_name = 'detail_product.html'
    
#商品の更新画面
class ProductUpdateView(LoginRequiredMixin, UpdateView):
    model = Products
    template_name = 'update_product.html'
    form_class = forms.ProductUpdateForm
    success_url = reverse_lazy('rakuten:product_list')
    
#商品の削除画面
class ProductDeleteView(LoginRequiredMixin, DeleteView):
    model = Products
    template_name = 'delete_product.html'
    success_url = reverse_lazy('rakuten:product_list')
    

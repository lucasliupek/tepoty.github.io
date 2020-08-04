from django.shortcuts import render, get_object_or_404, redirect
from blog.models import Post, Comment, CreditAquisition, ContentItem, Transactions, Wallet
from users.models import Follow, Profile
import sys
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count
from .forms import NewCommentForm
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from .forms import CreditAquisitionForm, TransactionsForm
from datetime import datetime
from django.conf import settings
from decimal import *
from django.urls import reverse
from paypal.standard.forms import PayPalPaymentsForm
from decimal import Decimal
from django.http import HttpResponseRedirect
from django.utils import timezone

def is_users(post_user, logged_user):
    return post_user == logged_user

PAGINATION_COUNT = 5

class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author')\
            .annotate(author_count=Count('author'))\
            .order_by('-author_count')[:5]

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())

        data['all_users'] = all_users
        if self.request.user:
            credits_owned = get_object_or_404(Wallet, user=self.request.user).balance
            data['credits'] = credits_owned
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        user = self.request.user
        return Post.objects.order_by('-date_posted')

class PostListFollowingView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author')\
            .annotate(author_count=Count('author'))\
            .order_by('-author_count')[:5]

        for aux in data_counter:
            all_users.append(User.objects.filter(pk=aux['author']).first())

        data['all_users'] = all_users
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATION_COUNT

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == '', file=sys.stderr)

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (Follow.objects.filter(user=logged_user,
                                                follow_user=visible_user).count() == 0)
        data = super().get_context_data(**kwargs)

        data['user_profile'] = visible_user
        data['can_follow'] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = Follow.objects.filter(user=request.user,
                                                    follow_user=self.visible_user())

            if 'follow' in request.POST:
                    new_relation = Follow(user=request.user, follow_user=self.visible_user())
                    if follows_between.count() == 0:
                        new_relation.save()
            elif 'unfollow' in request.POST:
                    if follows_between.count() > 0:
                        follows_between.delete()

        return self.get(self, request, *args, **kwargs)


class PostDetailView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)


class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post_new.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Add a new post'
        return data


class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post_new.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Edit a post'
        return data


class FollowsListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'follows'
        return data

class FollowersListView(LoginRequiredMixin, ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(User, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'
        return data

class CreditAquisitionView(LoginRequiredMixin, TemplateView):
    def credit_aquisition(request):
        if request.user.is_authenticated:
            if request.method == 'POST':
                form = CreditAquisitionForm(request.POST)
                if form.is_valid():
                    cleaned_data = form.cleaned_data
                    aquisition_register = CreditAquisition(
                        user = request.user,
                        amount = cleaned_data.get('amount'),
                        status = 'P',
                        operation_date = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f')
                    )
                    aquisition_register.save()

                    request.session['order_id'] = aquisition_register.id

                    messages.add_message(request, messages.INFO, 'Order Placed!')
                    return redirect('process_payment')
            else:
                form = CreditAquisitionForm()
                return render(request, 'blog/credit_aquisition.html', locals())
        else:
            return redirect('register-users')
class ProcessPaymentView(LoginRequiredMixin, TemplateView):
    def process_payment(request):
        CreditAquisition_id = request.session.get('order_id')
        ca = get_object_or_404(CreditAquisition, id=CreditAquisition_id)
        host = request.get_host()
    
        paypal_dict = {
            'business': settings.PAYPAL_RECEIVER_EMAIL,
            'amount': '%.2f' % Decimal(ca.amount).quantize(
                Decimal('.01')),
            'item_name': 'Order {}'.format(ca.id),
            'invoice': str(ca.id),
            'currency_code': 'BRL',
            'notify_url': 'http://{}{}'.format(host,
                                            reverse('paypal-ipn')),
            'return_url': 'http://{}{}'.format(host,
                                            reverse('payment_done')),
            'cancel_return': 'http://{}{}'.format(host,
                                                reverse('payment_cancelled')),
        }
    
        form = PayPalPaymentsForm(initial=paypal_dict)
        return render(request, 'blog/process_payment.html', {'CreditAquisition': ca, 'form': form})

class PaymentDoneView(LoginRequiredMixin, TemplateView):
    @csrf_exempt
    def payment_done(request):
        return render(request, 'blog/payment_done.html')

class PaymentCanceledView(LoginRequiredMixin, TemplateView):
    @csrf_exempt
    def payment_canceled(request):
        return render(request, 'blog/payment_cancelled.html')

class ContentItemView(LoginRequiredMixin, DetailView):
    model = Post
    template_name = 'blog/buy_content_item.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post_item = get_object_or_404(Post, id=self.get_object().id)
        if (post_item.content_item) and (post_item.content_item.item_price>0):
            print("post_item:")
            post_user = self.request.user
            transactions_obj_count = Transactions.objects.filter(user_from=post_user, user_to=post_item.author, content_item=post_item.content_item, status="A").count()
            if (post_item.author == post_user) or (transactions_obj_count >= 1):
                data['content_permission'] = True
            price_string = "R$ "+str(round(Decimal(self.get_object().content_item.item_price),2))
            data['price_string'] = price_string
            return data
            

class TransactionView(LoginRequiredMixin, TemplateView):
    #model = Post
    template_name = 'blog/transaction.html'
    #context_object_name = 'post'
    #success_url = success_url.get_sucess_url()
    
    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        post_id = data['pk']
        post_item = get_object_or_404(Post, id=post_id)
        content_item = get_object_or_404(ContentItem, id=post_item.content_item.id)
        #initial={'user_from': request.user, 'user_to': content_item.contentcreator,'amount': content_item.item_price, 'content_item': content_item.id}
        #print("data:")
        #print(data)
        print("data:")
        print(data)
        return data
        
    def post(self, request, pk, **kwargs):
        data = super().get_context_data(**kwargs)
        post_id = pk
        post_item = get_object_or_404(Post, id=post_id)
        content_item = get_object_or_404(ContentItem, id=post_item.content_item.id)
        wallet_from = get_object_or_404(Wallet, user=request.user)
        wallet_to = get_object_or_404(Wallet, user=post_item.author)
        if wallet_from.balance >= content_item.item_price:
            
            transaction_register = Transactions(
                user_from = request.user,
                user_to = post_item.author,
                amount = content_item.item_price,
                content_item = content_item,
                status = 'A',
                operation_date = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f',
                )
            )
            transaction_register.save()
            transaction_time = timezone.now()
            wallet_from.balance = wallet_from.balance - content_item.item_price
            wallet_from.last_updated = transaction_time
            wallet_from.save()
            wallet_to.balance = wallet_to.balance + content_item.item_price
            wallet_to.last_updated = transaction_time
            wallet_to.save()
            messages.add_message(request, messages.INFO, 'Purchase sucessfull!')
            url = '/post/{}/'.format(str(post_id))
        else:
            transaction_register = Transactions(
                user_from = request.user,
                user_to = post_item.author,
                amount = content_item.item_price,
                content_item = content_item,
                status = 'D',
                operation_date = datetime.strptime(str(datetime.now()), '%Y-%m-%d %H:%M:%S.%f',
                )
            )
            transaction_register.save()
            messages.add_message(request, messages.INFO, 'Not enought credits!')
            url = '/credit-aquisition/'
        
        return HttpResponseRedirect(url)

class PostCreateView(LoginRequiredMixin, TemplateView):
    model = Post
    fields = ['content', '']
    template_name = 'blog/post_new.html'
    success_url = '/'

    def post(self, request, pk, **kwargs):
        data = super().get_context_data(**kwargs)
        post_id = pk
        post_item = get_object_or_404(Post, id=post_id)
        content_item = get_object_or_404(ContentItem, id=post_item.content_item.id)
        wallet_from = get_object_or_404(Wallet, user=request.user)
        wallet_to = get_object_or_404(Wallet, user=post_item.author)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Add a new post'
        return data
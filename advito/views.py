from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader_tags import register
from django.urls import reverse
from django.utils import timezone
from django.template import loader
from django.utils.decorators import method_decorator
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView, View
from .exceptions import PermissionDenied
from .forms import SignupForm, LoginForm, UpdateProfileForm, MessageForm
from advito.models import Profile, Chat, Message




# class DialogsView(View):
#     def get(self, request):
#         chats = Chat.objects.filter(members__in=[request.user.id])
#         return render(request, 'users/dialogs.html', {'user_profile': request.user, 'chats': chats})


class IndexView(ListView):
    '''
    вьюха для главной страницы
    '''
    model = Profile
    template_name = 'advito/index.html'
    context_object_name = 'users'

    def get_queryset(self):
        return Profile.objects.all()


class PeopleView(ListView):
    '''
    вьюха для главной страницы
    '''
    model = Profile
    template_name = 'advito/people.html'
    context_object_name = 'users'

    def get_queryset(self):
        return Profile.objects.all()


from django.contrib.auth.views import LoginView
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView


class LoginView(LoginView):
    template_name = 'my_auth/login.html'
    form_class = LoginForm

    def post(self, request, *args, **kwargs):
        form = self.form_class(data=request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect(reverse('index'), request)
            else:
                context = {}
                context['form'] = form
                return render(request=request, template_name=self.template_name, context=context)
        else:
            context = {'form': form}
            return render(request=request, template_name=self.template_name, context=context)


class ProfileView(DetailView):
    model = Profile
    template_name = 'advito/profile.html'

    def get_object(self):
        return get_object_or_404(Profile, user__id=self.kwargs['user_id'])


@login_required
def logout_view(request):
    logout(request)
    return redirect(reverse("index"))


class SignupView(View):
    template_name = 'my_auth/signup.html'
    registration_form = SignupForm

    def get(self, request, *args, **kwargs):
        context = {'form': self.registration_form}
        return render(request=request, template_name=self.template_name, context=context)

    def post(self, request, *args, **kwargs):
        user_form = SignupForm(data=request.POST)
        registered = False
        if user_form.is_valid():
            user = user_form.save(commit=True)
            user.email = user_form.cleaned_data['email']
            user.save()
            registered = True
            return render(request, 'my_auth/signup.html',
                          {'registered': registered})
        else:
            return render(request, 'my_auth/signup.html',
                          {'form': user_form,
                           'registered': registered})


class EditProfileView(UpdateView):
    model = Profile
    form_class = UpdateProfileForm
    template_name = 'advito/edit_profile.html'
    slug_field = "user_id"
    slug_url_kwarg = "user_id"

    def dispatch(self, request, *args, **kwargs):
        obj = self.get_object()
        if obj.user != self.request.user:
            raise Http404("It is not your profile!")
        return super(EditProfileView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        user_id = self.kwargs['user_id']
        return reverse('profile', args=(user_id,))


class DialogsView(View):
    def get(self, request):
        chats = Chat.objects.filter(members__in=[request.user.id])
        return render(request, 'advito/dialogs.html', {'user_profile': request.user, 'chats': chats})


class MessagesView(View):
    def get(self, request, chat_id):
        try:
            chat = Chat.objects.get(id=chat_id)
            if request.user in chat.members.all():
                chat.message_set.filter(is_readed=False).exclude(author=request.user).update(is_readed=True)
            else:
                chat = None
        except Chat.DoesNotExist:
            chat = None

        return render(
            request,
            'advito/messages.html',
            {
                'user_profile': request.user,
                'chat': chat,
                'form': MessageForm()
            }
        )

    def post(self, request, chat_id):
        form = MessageForm(data=request.POST)
        if form.is_valid():
            message = form.save(commit=False)
            message.chat_id = chat_id
            message.author = request.user
            message.save()
        return redirect(reverse('messages', kwargs={'chat_id': chat_id}))


class CreateDialogView(View):
    def get(self, request, user_id):
        chats = Chat.objects.filter(members__in=[request.user.id, user_id], type=Chat.DIALOG)
        if chats.count() == 0:
            chat = Chat.objects.create()
            chat.members.add(request.user)
            chat.members.add(user_id)
        else:
            chat = chats.first()
        return redirect(reverse('messages', kwargs={'chat_id': chat.id}))


@register.simple_tag
def get_companion(user, chat):
    for u in chat.members.all():
        if u != user:
            return u
    return None
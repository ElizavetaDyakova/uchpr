from django.db import models
from django.contrib.auth.models import User
from django.db.models import Count
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.views import View


def ava_path(instance, filename):
    return 'user_{0}/avas/{1}'.format(instance.user.id, filename)




class Profile(models.Model):
    '''
    Модель пользователя
    '''
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_profile')
    birth_date = models.DateField('Date of birth', null=True, blank=True)
    about = models.TextField('About', max_length=500, blank=True)
    ava = models.ImageField(upload_to=ava_path, default=None)
    phone_number = models.CharField(max_length=12, default=None)

    def __str__(self):
        return str(self.user.username)


class Chat(models.Model):
    DIALOG = 'D'
    CHAT = 'C'
    CHAT_TYPE_CHOICES = (
        (DIALOG, _('Dialog')),
        (CHAT, _('Chat'))
    )

    type = models.CharField(
        _('Тип'),
        max_length=1,
        choices=CHAT_TYPE_CHOICES,
        default=DIALOG
    )
    members = models.ManyToManyField(User, verbose_name=_("Участник"))

    def get_absolute_url(self):
        return 'messages', (), {'chat_id': self.pk}


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.PROTECT, verbose_name=_("Чат"))
    author = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name=_("Пользователь"))
    message = models.TextField(_("Сообщение"))
    image = models.ImageField(upload_to=ava_path, blank=True)
    pub_date = models.DateTimeField(_('Дата сообщения'), default=timezone.now)
    is_readed = models.BooleanField(_('Прочитано'), default=False)

    class Meta:
        ordering = ['pub_date']

    def __str__(self):
        return self.message


class CreateDialogView(View):
    def get(self, request, user_id):
        chats = Chat.objects.filter(members__in=[request.user.id, user_id], type=Chat.DIALOG).annotate(c=Count('members')).filter(c=2)
        if chats.count() == 0:
            chat = Chat.objects.create()
            chat.members.add(request.user)
            chat.members.add(user_id)
        else:
            chat = chats.first()
        return redirect(reverse('advito:messages', kwargs={'chat_id': chat.id}))


def add_path():
    return None
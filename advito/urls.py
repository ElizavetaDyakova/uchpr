from django.conf.urls import url
from advito import views
from django.urls import path, reverse_lazy
from django.views.generic import TemplateView
from advito.views import SignupView, LoginView, EditProfileView, ProfileView, logout_view
from django.contrib.auth.decorators import login_required



urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    path('<int:user_id>/profile/', ProfileView.as_view(), name='profile'),
    path('dialogs/', login_required(views.DialogsView.as_view()), name='dialogs'),
    path('<user_id>/dialogs/create/', login_required(views.CreateDialogView.as_view()), name='create_dialog'),
    path('people/', views.PeopleView.as_view(), name='people'),
    path('dialogs/<chat_id>/', login_required(views.MessagesView.as_view()), name='messages'),

]

from django.contrib.auth.views import PasswordResetDoneView, PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns += [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', logout_view, name='logout'),
    path('<int:user_id>/profile/edit', login_required(EditProfileView.as_view()), name='edit-profile'),
    path('signup/', SignupView.as_view(), name='signup'),
    path('password_reset/', PasswordResetView.as_view(success_url=reverse_lazy('users:password_reset_done'),
                                                      template_name='my_auth/password_reset.html'),
         name='password_reset'),

    path('password_reset/done', PasswordResetDoneView.as_view(template_name='my_auth/password_reset_done.html'),
         name='password_reset_done'),

    path('password_reset/<str:uidb64>/<slug:token>', PasswordResetConfirmView.as_view(
        success_url=reverse_lazy('users:password_reset_complete')), name='password_reset_confirm'),

    path('password_reset/complete', PasswordResetCompleteView.as_view(), name='password_reset_complete')
]
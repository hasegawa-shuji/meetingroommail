from django import forms
from allauth.account.forms import SignupForm

#サインアップ用フォーム保存完了時に認証メールを送信
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_bytes, force_text
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser
# from django.contrib.auth import get_user_model
# CustomUser = get_user_model()


class ProfileForm(forms.Form):
    first_name = forms.CharField(max_length=30, label='姓')
    last_name = forms.CharField(max_length=30, label='名')
    description = forms.CharField(label='自己紹介', widget=forms.Textarea(), required=False)
    image = forms.ImageField(required=False, )


class SignupUserForm(SignupForm):
    first_name = forms.CharField(max_length=30, label='姓')
    last_name = forms.CharField(max_length=30,  label='名')

    def save(self, request):
        user = super().save(request)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        return user


#サインアップメール送信設定
subject = "登録確認"
message_template = """
ご登録ありがとうございます。
以下URLをクリックして登録を完了してください。

"""
#サインアップメール送信設定
def get_activate_url(user):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    return settings.FRONTEND_URL + "activate/{}/{}/".format(uid, token)


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'password1', 'password2')
    
    def save(self, commit=True):
        # commit=Falseだと、DBに保存されない
        user = super().save(commit=False)
        # user.first_name = self.cleaned_data['first_name']
        # user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data["email"]
        # user.password1 = self.cleaned_data['password1']
        # user.password2 = self.cleaned_data['password2']

        # 確認するまでログイン不可にする
        user.is_active = False

        if commit:
            user.save()
            activate_url = get_activate_url(user)
            message = message_template + activate_url
            # from_email = "admin@itc.tokyo"
            # recipient_list =["test@itc.tokyo"]
            user.email_user(subject, message)
        return user


#サインアップメール認証設定
def activate_user(uidb64, token):    
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except Exception:
        return False

    if default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        return True
    
    return False
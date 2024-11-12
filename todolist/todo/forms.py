from django import forms
from .models import Todo
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class TodoForm(forms.ModelForm):
    class Meta:
        model = Todo
        fields = ['title', 'description', 'important', 'deadline']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control'}),
            'deadline': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.deadline:
            # 기존 deadline 값을 datetime-local 입력에 맞는 형식으로 변환
            self.initial['deadline'] = self.instance.deadline.strftime('%Y-%m-%dT%H:%M')
        
        

class CustomUserCreationForm(UserCreationForm):
    nickname = forms.CharField(max_length=50)
    character = forms.ChoiceField(choices=[
        ('char1', 'Character 1'),
        ('char2', 'Character 2'),
        ('char3', 'Character 3'),
    ], widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('nickname', 'username', 'password1', 'password2', 'character')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.character_images = {
            'char1': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEisDy2OZcb2ys4Hd7eCNf2PW5-VhcyOPiVGgG29ftptAUc0j7VmahVZ4Ne7lzj9Ty79at-SDWxKHGNHHrtRNx02pRnyRscF6ZDvm2oFqEOBQiIMUfM8n4lu7dqTF2c6gi48Zxz2EWa40KLXQTCQ2OvMaetQipNuccyujXIdtk97R-rq1tnrlt3pNVHMOxSs/s320/char1.jpg",
            'char2': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEg8mO5R62gO068Y3jcc5nXgEJ5fTes4l2dNW9Gfiz-w9Sd5kh2u4LKj22-6P_quOVoXs3C3YoxpmmU1K8D3THHkawSGKTkx1EitF13Qy-86W2qA_s1_H3uzHnV4sR8khnLVsqlC7fGD7izXzPJutdRL3uWHzj75jUW4B52OIWfD2f6iKDKnmxkGM62BSQwM/s320/Char2.jpg",
            'char3': "https://blogger.googleusercontent.com/img/b/R29vZ2xl/AVvXsEjuBWeWD6ybcYqdmgB7X7g88c2zQ1OrAB8bFFi3LQolQyKaYKLVnr-zdLrf0V8c4m6-ePpOdEkLGlZieXyEliqnkG-wICfApL5RTjQLHWzQtYZqDur39U6_fy_xFKAVPuiAzPmTAZNLUiW5dk6c0EzpD6NKnYUiJV0pAcIZ1A-OVkwJJANen2rSV2qfdcJC/s320/Char3.jpg",
        }

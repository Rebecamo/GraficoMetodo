from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Problema

class RegistroFormPersonalizado(UserCreationForm):
    #Formulario de registro personalizado que incluye nombre, apellido y correo electrónico.
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label="Nombre",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre'
        })
    )

    last_name = forms.CharField(
        max_length=30,
        required=True,
        label="Apellido",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apellido'
        })
    )

    email = forms.EmailField(
        max_length=254,
        required=True,
        label="Correo electrónico",
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )

    username = forms.CharField(
        max_length=150,
        required=True,
        label="Nombre de usuario",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Nombre de usuario'
        }),
        help_text='',
    )

    password1 = forms.CharField(
        label="Contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        }),
        help_text='',
    )

    password2 = forms.CharField(
        label="Confirmar contraseña",
        strip=False,
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        }),
        help_text='',
    )

    class Meta:
        model = User
        fields = (
            "first_name", "last_name", "email", "username", "password1", "password2"
        )


class ProblemaForm(forms.ModelForm):
    #Formulario basado en el modelo Problema. Usa solo los campos definidos en el modelo actual.
    class Meta:
        model = Problema
        fields = ['objetivo', 'funcion_objetivo', 'restricciones', 'limites']
        widgets = {
            'objetivo': forms.Select(attrs={'class': 'form-select'}),
            'funcion_objetivo': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: 3x + 4y'
            }),
            'restricciones': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Ej:\n2x + 3y <= 6\nx + y <= 4'
            }),
            'limites': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Ej: x >= 0, y >= 0'
            }),
        }

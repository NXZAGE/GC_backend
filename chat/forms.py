from django import forms


class MessageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea(
        attrs={'class': 'message_area',
               'placeholder': 'Enter Message'}
    ))

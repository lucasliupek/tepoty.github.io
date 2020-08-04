from django import forms
from .models import Comment, CreditAquisition, Transactions 


class NewCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']

class CreditAquisitionForm(forms.ModelForm):
    class Meta:
        model = CreditAquisition
        exclude = ('status', 'user', 'operation_date')

        widgets = {
            'amount': forms.NumberInput(),
        }

class TransactionsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs): 
        super(TransactionsForm, self).__init__(*args, **kwargs)                       
        self.fields['user_from'].disabled = True
        self.fields['user_to'].disabled = True
        self.fields['amount'].disabled = True
        self.fields['content_item'].disabled = True
        self.fields['user_from'] = 1
        self.fields['user_to'] = 2
        self.fields['amount'] = 1
        self.fields['content_item'] = 1
    class Meta:
        model = Transactions
        exclude = ('status', 'operation_date')
        
        

    
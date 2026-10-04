import re
from django import forms
from .models import Consultation


class ConsultationForm(forms.ModelForm):
    class Meta:
        model = Consultation
        fields = ['name', 'phone', 'subject', 'message']

    def clean_name(self):
        name = self.cleaned_data['name'].strip()
        if len(name) < 2:
            raise forms.ValidationError('نام را کامل وارد کنید.')
        return name

    def clean_phone(self):
        raw = self.cleaned_data['phone'].strip().translate(str.maketrans(
            '۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩', '01234567890123456789'
        ))
        phone = re.sub(r'[\s()\-–]', '', raw)
        if not re.fullmatch(r'\+?\d{10,15}', phone):
            raise forms.ValidationError('شماره تماس معتبر وارد کنید.')
        return phone

    def clean_message(self):
        return self.cleaned_data['message'].strip()

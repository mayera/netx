from django import forms

class UploadForm(forms.Form):
    inpfoptions=[()]
    inpformat=forms.ChoiceField(label="format",choices=inpfoptions,required=False)
    pathn=forms.CharField(max_length=500,required=True)


class pathviewform(forms.Form):
    foptions=[('jpg','jpg'),('png','png'),('gif','gif'),('bmp','bmp'),('svg','svg'),
              ('dot','dot'),('eps','eps'),('ps','ps'),('pdf','pdf')]
    poptions=[('dot','dot'),('neato','neato'),('twopi','twopi'),('circo','circo'),('fdp','fdp')]
    fformat=forms.ChoiceField(label="format", choices=foptions,required=False)
    prog=forms.ChoiceField(label="program", choices=poptions,required=False)
#    rlabel=forms.BooleanField(label="reaction label",required=False)
#    mlabel=forms.BooleanField(label="metabolite label",required=False)



class netdispform(forms.Form):
    foptions=[('jpg','jpg'),('png','png'),('gif','gif'),('bmp','bmp'),('svg','svg'),
              ('dot','dot'),('eps','eps'),('ps','ps'),('pdf','pdf')]
    poptions=[('dot','dot'),('neato','neato'),('twopi','twopi'),('circo','circo'),('fdp','fdp')]
    fformat=forms.ChoiceField(label="format", choices=foptions,required=False)
    layout=forms.ChoiceField(label="layout", choices=poptions,required=False)

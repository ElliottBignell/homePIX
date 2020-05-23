from django import forms
from blog.models import Comment, Directory, PictureFile, Keywords, Album, AlbumContent

class AlbumForm( forms.ModelForm ):

    #thumbnail = forms.ModelChoiceField( queryset = PictureFile.objects.all() )

    class Meta():
        model = Album
        fields = ( 'name', 'thumbnail' )

        widgets = {
            'path' : forms.TextInput( attrs={ 'class': 'textinputclass' })
        }

class AlbumContentForm( forms.ModelForm ):

    class Meta():
        model = AlbumContent
        fields = ( 'album', 'entry' )

        widgets = {
            'album' : forms.TextInput( attrs={ 'class': 'textinputclass' }),
            'entry' : forms.TextInput( attrs={ 'class': 'textinputclass' })
        }

class AlbumAddForm( forms.ModelForm ):
    add_to_album = forms.CharField( required = True )

class DirectoryForm( forms.ModelForm ):

    class Meta():
        model = Directory
        fields = ( 'path',  )

        widgets = {
            'path' : forms.TextInput( attrs={ 'class': 'textinputclass' })
        }

class PictureForm( forms.ModelForm ):

    class Meta():
        model = PictureFile
        fields = ( 'path', 'file', 'title' )

        widgets = {
            'title': forms.TextInput( attrs={ 'class': 'textinputclass' } ),
            'path' : forms.TextInput( attrs={ 'class': 'textinputclass' }),
            'file' : forms.TextInput( attrs={ 'class': 'textinputclass' })
        }

class PictureSearchForm( forms.ModelForm ):
    search = forms.CharField( required = False )

class CommentForm( forms.ModelForm ):

    class Meta():
        model = Comment
        fields = ( 'author', 'text' )

        widgets = {
            'author': forms.TextInput( attrs={ 'class': 'textinputclass' } ),
            'text': forms.Textarea( attrs={ 'class': 'editable medium-editor-textarea' })
        }

class KeywordsForm( forms.ModelForm ):

    class Meta():
        model = Keywords
        fields = ( 'keywords',  )

        widgets = {
            'keywords' : forms.TextInput( attrs={ 'class': 'textinputclass' })
        }

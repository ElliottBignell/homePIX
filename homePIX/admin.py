from django.contrib import admin
from blog.models import Directory, Comment, PictureFile, Keywords

# Register your models here.
admin.site.register( Comment )
admin.site.register( PictureFile )
admin.site.register( Directory )
admin.site.register( Keywords )

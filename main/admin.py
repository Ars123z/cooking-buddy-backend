from django.contrib import admin
from django.db import models
from django.contrib.admin.widgets import FilteredSelectMultiple
from django import forms

from main.models import PlayList, Video, WatchHistory, Labels

# Register your models here.

admin.site.register(PlayList)
admin.site.register(WatchHistory)

class VideoFilteredSelectMultiple(FilteredSelectMultiple): 
    def __init__(self, *args, **kwargs): 
        super().__init__(*args, **kwargs)

    def build_attrs(self, base_attrs, extra_attrs=None): 
        attrs = dict(base_attrs, **(extra_attrs or {})) 
        attrs['class'] = attrs.get('class', '') + ' admin-video-filtered-select-multiple'
        return attrs
    
    def render(self, name, value, attrs=None, renderer=None): 
        attrs = self.build_attrs(attrs) 
        return super().render(name, value, attrs, renderer)
    
class LabelAdminForm(forms.ModelForm):      
    class Meta: 
        model = Labels 
        fields = '__all__'
        videos = forms.ModelMultipleChoiceField( queryset=Video.objects.all(), widget=VideoFilteredSelectMultiple('videos', is_stacked=False) )

    class Media:
        css = {
            'all': ('/static/admin/css/widgets.css',),
        }
        js = ('/admin/jsi18n/',)

class VideoAdmin(admin.ModelAdmin):
    list_display = ('title',)
    search_fields = ('title',)

class LabelAdmin(admin.ModelAdmin):
    form = LabelAdminForm
    list_display = ('name', 'region', 'last_updated')
    filter_horizontal = ('videos',)

admin.site.register(Video, VideoAdmin)
admin.site.register(Labels, LabelAdmin)
    
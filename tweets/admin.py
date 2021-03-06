from django.contrib import admin
from tweets.models import Tweet

# Register your models here.
@admin.register(Tweet)
class TweetAdmin(admin.ModelAdmin):
    # date_hierarchy = 'created_at'
    list_display = (
        'winnipeg_time',
        'created_at',
        'user',
        'content',
        'hours_to_now',
    )
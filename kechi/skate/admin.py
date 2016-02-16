from django.contrib import admin

# Register your models here.
import skate.models

# Register your models here.

admin.site.register(skate.models.Store)
admin.site.register(skate.models.Item)
admin.site.register(skate.models.CommPreferences)

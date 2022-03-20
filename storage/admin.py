from django.contrib import admin

from .models import GraphicCard


@admin.register(GraphicCard)
class GraphicCardAdmin(admin.ModelAdmin):
    pass

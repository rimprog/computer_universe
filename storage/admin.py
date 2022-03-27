from django.contrib import admin

from .models import GraphicCard
from .models import TelegramUser


@admin.register(GraphicCard)
class GraphicCardAdmin(admin.ModelAdmin):
    pass


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    pass

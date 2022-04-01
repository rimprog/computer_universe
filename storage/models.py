from django.db import models


class GraphicCard(models.Model):
    name = models.CharField('имя', max_length=200)
    url = models.URLField('ссылка')
    current_eur_price = models.FloatField('текущая цена EUR')
    current_rub_price = models.FloatField('текущая цена RUB', null=True, blank=True)
    old_price = models.FloatField('старая цена', null=True, blank=True)
    price_notification_request = models.BooleanField('уведомить пользователей об изменении цены', default=False, blank=True)

    class Meta:
        verbose_name = 'видеокарта'
        verbose_name_plural = 'видеокарты'

    def __str__(self):
        return self.name


class TelegramUser(models.Model):
    telegram_id = models.CharField('телеграм id', max_length=200)
    is_active = models.BooleanField('учетная запись активирована', default=False)
    min_price = models.FloatField('минимальная цена видеокарты к показу', null=True, blank=True)
    max_price = models.FloatField('максимальная цена видеокарты к показу', null=True, blank=True)

    class Meta:
        verbose_name = 'пльзователь телеграм'
        verbose_name_plural = 'пользователи телеграма'

    def __str__(self):
        return self.telegram_id

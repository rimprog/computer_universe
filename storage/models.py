from django.db import models


class GraphicCard(models.Model):
    name = models.CharField('имя', max_length=200)
    url= models.URLField('ссылка')
    old_price = models.FloatField('старая цена')
    current_eur_price = models.FloatField('текущая цена EUR')
    current_rub_price = models.FloatField('текущая цена RUB')

    class Meta:
        verbose_name = 'видеокарта'
        verbose_name_plural = 'видеокарты'

    def __str__(self):
        return self.name

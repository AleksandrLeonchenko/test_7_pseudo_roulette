from django.db import models
from django.db.models import Avg, Count
from django.contrib.auth.models import User


class RouletteRound(models.Model):
    """
    Содержит информацию о номере раунда рулетки, о пользователях, флаг завершения раунда,
    количестве прокручиваний рулетки в раунде.
    """
    users = models.ManyToManyField(
        User,
        related_name='rounds',
        verbose_name='Участвующие пользователи'
    )
    round_number = models.IntegerField(
        unique=True,
        null=True,
        verbose_name='Номер раунда'
    )
    is_round_finished = models.BooleanField(
        default=False,
        verbose_name='Раунд завершен'
    )
    number_roulette_spins_round = models.IntegerField(
        default=0,
        verbose_name='Количество прокручиваний рулетки в раунде'
    )
    num_users = models.IntegerField(
        default=0,
        verbose_name='Количество пользователей в раунде'
    )

    def __str__(self):
        return f"Раунд {self.round_number}"

    class Meta:
        verbose_name = 'Раунд рулетки'
        verbose_name_plural = 'Раунды рулетки'
        ordering = ['pk']


class RouletteSpin(models.Model):
    """
    Хранит информацию о каждом вращении рулетки, пользователе, который вращает рулетку,
    номере раунда, номере выпавшей ячейки, количестве прокручиваний рулетки и о временной метке события.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        default=1,
        verbose_name='Пользователь'
    )
    round_number = models.ForeignKey(
        RouletteRound,
        on_delete=models.CASCADE,
        related_name='spins',
        verbose_name='Раунд рулетки'
    )
    spun_cell = models.IntegerField(
        verbose_name='Номер выпавшей ячейки'
    )
    number_roulette_spins = models.IntegerField(
        default=0,
        verbose_name='На этом прокручивании выпала ячейка'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Временная метка'
    )

    def __str__(self):
        return f"Вращение {self.number_roulette_spins} в раунде {self.round_number}"

    class Meta:
        verbose_name = 'Вращение рулетки'
        verbose_name_plural = 'Вращения рулетки'
        ordering = ['pk']


class UserStatistics(models.Model):
    """
    Модель для хранения статистики пользователя в рулетке.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        primary_key=True,
        verbose_name='Пользователь'
    )
    num_rounds_participated = models.IntegerField(
        default=0,
        verbose_name='Количество раундов участия в рулетке'
    )
    avg_spins_per_round = models.FloatField(
        default=0,
        verbose_name='Среднее количество прокручиваний рулетки за раунд'
    )

    def __str__(self):
        return f"Статистика пользователя {self.user}"

    class Meta:
        verbose_name = 'Статистика пользователя'
        verbose_name_plural = 'Статистика пользователей'

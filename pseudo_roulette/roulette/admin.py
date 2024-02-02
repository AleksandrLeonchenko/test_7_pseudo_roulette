from django.contrib import admin
from .models import RouletteRound, RouletteSpin, UserStatistics


@admin.register(RouletteRound)
class RouletteRoundAdmin(admin.ModelAdmin):
    list_display = ('id', 'round_number',)
    list_display_links = ('id', 'round_number',)
    search_fields = ('id', 'round_number',)


@admin.register(RouletteSpin)
class RouletteSpinAdmin(admin.ModelAdmin):
    list_display = ('id', 'round_number', 'user', 'spun_cell', 'number_roulette_spins', 'timestamp')
    list_display_links = ('id', 'round_number', 'user', 'spun_cell', 'number_roulette_spins', 'timestamp')
    search_fields = ('id', 'round_number__user__username', 'round_number__round_number', 'spun_cell')


@admin.register(UserStatistics)
class UserStatisticsAdmin(admin.ModelAdmin):
    list_display = ('user',)
    list_display_links = ('user',)
    search_fields = ('user__username',)


admin.site.site_header = 'Админ-панель проекта "pseudo_roulette"'
admin.site.site_header = 'Админ-панель проекта "pseudo_roulette"'
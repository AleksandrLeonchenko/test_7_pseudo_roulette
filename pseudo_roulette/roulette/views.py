import json
import random

from django.contrib.auth.decorators import login_required
from django.db.models import Avg, Count
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, logout

from django.views import View

from .models import RouletteRound, RouletteSpin, UserStatistics
from .service import spin_roulette


class RegisterUserView(View):
    """
    Вью для регистрации нового пользователя.

    Attributes:
    - template_name (str): Название шаблона для отображения страницы регистрации.
    """
    template_name = 'roulette/register.html'

    def get(self, request, *args, **kwargs):
        """
        Обработчик GET-запроса для отображения формы регистрации.

        Returns:
        - HttpResponse: Ответ с отображением формы регистрации.
        """
        form = UserCreationForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """
        Обработчик POST-запроса для обработки данных формы регистрации.

        Returns:
        - HttpResponse: Редирект на страницу статистики участников рулетки в случае успешной регистрации.
        """
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('roulette-participants')
        return render(request, self.template_name, {'form': form})


@method_decorator(csrf_exempt, name='dispatch')
class SpinRouletteView(View):
    """
    Вью для прокрутки рулетки.
    Пример запроса: {"user_id": 1}

    Attributes:
    - Allowed methods: POST
    """

    def post(self, request, *args, **kwargs):
        """
        Обработчик POST-запроса для прокрутки рулетки.

        Returns:
        - JsonResponse: JSON-ответ с номером выбранной ячейки.
        """
        try:
            json_data = json.loads(request.body)
            user_id = json_data.get("user_id")
        except (ValueError, AttributeError, TypeError):
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        chosen_cell = spin_roulette(user_id)
        response_data = {'chosen_cell': chosen_cell}
        return JsonResponse(response_data)


class RouletteParticipantsView(View):
    """
    Вью для получения статистики участников рулетки.

    Attributes:
    - Allowed methods: GET
    """
    def get(self, request, *args, **kwargs):
        """
        Обработчик GET-запроса для получения статистики участников рулетки.

        Returns:
        - JsonResponse: JSON-ответ с данными о количестве участников в каждом раунде.
        """
        rounds = RouletteRound.objects.all()
        statistics = {}  # Словарь для хранения статистики
        for round in rounds:
            statistics[round.round_number] = round.num_users
        return JsonResponse(statistics)


class ActiveUsersView(View):
    """
    Вью для получения статистики активных пользователей.

    Attributes:
    - Allowed methods: GET
    """
    def get(self, request, *args, **kwargs):
        """
        Обработчик GET-запроса для получения статистики активных пользователей.

        Returns:
        - JsonResponse: JSON-ответ с данными о количестве раундов и среднем количестве прокручиваний рулетки
        за раунд для каждого пользователя.
        """
        user_statistics = UserStatistics.objects.all()
        data = {}  # Словарь для хранения данных
        for user_stat in user_statistics:
            user_id = user_stat.user.id
            data[user_id] = [
                {"num_rounds_participated": user_stat.num_rounds_participated},
                {"avg_spins_per_round": user_stat.avg_spins_per_round}
            ]

        return JsonResponse(data)

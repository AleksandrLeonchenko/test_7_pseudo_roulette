import random

from django.contrib.auth.models import User
from django.db.models import F, Max, Count, Avg
from django.db.models.functions import Round
from django.shortcuts import get_object_or_404

from .models import RouletteRound, RouletteSpin, UserStatistics


def spin_roulette(user_id: int) -> int:
    """
    Вращает рулетку для указанного пользователя и возвращает выпавшую ячейку.

    Parameters:
    - user_id (int): Идентификатор пользователя.

    Returns:
    - int: Номер выпавшей ячейки.
    """
    current_round = RouletteRound.objects.filter(is_round_finished=False).first()

    # Если нет не завершенного раунда, создаем новый
    if not current_round:
        current_round = RouletteRound.objects.create(is_round_finished=False)
        current_round.round_number = generate_next_round_number()
        current_round.save()

    user = get_object_or_404(User, pk=user_id)
    current_round.users.add(user)
    user_rounds_count = RouletteRound.objects.filter(users=user).count()
    if user_rounds_count > 1:  # Условие, определяющее САМЫХ активных пользователей

        average_spins_per_round = RouletteSpin.objects.filter(user=user).aggregate(
            average_spins=Round(Avg('number_roulette_spins'), 2)
        )['average_spins']
        statistics, created = UserStatistics.objects.update_or_create(
            user=user,
            defaults={
                'num_rounds_participated': user_rounds_count,
                'avg_spins_per_round': average_spins_per_round
            },
        )

    spun_cell = generate_spun_cell()  # Генерируем случайное число
    spin_exists = RouletteSpin.objects.filter(round_number=current_round, spun_cell=spun_cell).exists()
    RouletteRound.objects.filter(id=current_round.id).update(
        number_roulette_spins_round=F('number_roulette_spins_round') + 1
    )
    while spin_exists or (spun_cell == 11 and not checking_round_jackpot_conditions(current_round, 10)):
        spun_cell = generate_spun_cell()
        spin_exists = RouletteSpin.objects.filter(round_number=current_round, spun_cell=spun_cell).exists()
        RouletteRound.objects.filter(id=current_round.id).update(
            number_roulette_spins_round=F('number_roulette_spins_round') + 1
        )
        current_round.refresh_from_db()
    number_roulette_spins = current_round.number_roulette_spins_round
    roulette_spin = RouletteSpin.objects.create(
        round_number=current_round,
        user=User.objects.get(pk=user_id),
        spun_cell=spun_cell,
        number_roulette_spins=number_roulette_spins
    )
    round_number_value = current_round.round_number
    round_instance = RouletteRound.objects.get(round_number=round_number_value)  # Получаем раунд по номеру
    # users_in_round = round_instance.users.all()  # Получаем всех пользователей, участвовавших в данном раунде
    users_count = round_instance.users.count()  # Получаем количество пользователей, участвовавших в данном раунде
    round_instance.num_users = users_count
    round_instance.save()

    numbers_present = checking_round_jackpot_conditions(current_round, 11)
    if numbers_present:
        current_round = RouletteRound.objects.update(is_round_finished=True)
    return spun_cell


def generate_spun_cell() -> int:
    """
    Генерирует номер выпавшей ячейки на основе таблицы весов вероятности.
    Добавлен вес для ячейки 11, как средний вес ячеек 1...10.

    Returns:
    - int: Номер выпавшей ячейки.
    """
    weights = {
        1: 20,
        2: 100,
        3: 45,
        4: 70,
        5: 15,
        6: 140,
        7: 20,
        8: 20,
        9: 140,
        10: 45,
        11: 60,
    }

    return random.choices(list(weights.keys()), weights=list(weights.values()))[0]


def checking_round_jackpot_conditions(x: RouletteRound, y: int) -> bool:
    """
    Проверяет условие при котором возможен джекпот и смена раундов.

    Parameters:
    - x (RouletteRound): Экземпляр раунда.
    - y (int): Верхний предел значения ячейки.

    Returns:
    - bool: True, если условие выполнено, иначе False.
    """
    numbers_present = RouletteSpin.objects.filter(
        round_number=x,  # Условие для номера раунда
    ).values('spun_cell').annotate(count=Count('spun_cell')).filter(
        count=1,
        spun_cell__gte=1,
        spun_cell__lte=y
    ).count() == y  # Должно быть ровно 10 (или 11) уникальных значений
    return numbers_present


def generate_next_round_number() -> int:
    """
    Назначает номер для нового раунда.

    Returns:
    - int: Новый номер раунда.
    """
    # Получаем максимальный номер раунда
    max_round_number = RouletteRound.objects.aggregate(Max('round_number'))['round_number__max']
    if max_round_number is None:  # Если нет раундов, начинаем с 1
        return 1
    return max_round_number + 1  # Иначе возвращаем следующий номер

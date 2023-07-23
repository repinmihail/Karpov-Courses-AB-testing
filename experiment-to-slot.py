import numpy as np
import pandas as pd
import hashlib


class ABSplitter:
    def __init__(self, count_slots, salt_one, salt_two):
        self.count_slots = count_slots
        self.salt_one = salt_one
        self.salt_two = salt_two

        self.slots = np.arange(count_slots)
        self.experiments = []
        self.experiment_to_slots = dict()
        self.slot_to_experiments = dict()

    def split_experiments(self, experiments):
        """
        Устанавливает множество экспериментов, распределяет их по слотам.

        Нужно определить атрибуты класса:
            self.experiments - список словарей с экспериментами
            self.experiment_to_slots - словарь, {эксперимент: слоты}
            self.slot_to_experiments - словарь, {слот: эксперименты}
            
        experiments - список словарей, описывающих пилот. Словари содержит три ключа:
            experiment_id - идентификатор пилота,
            count_slots - необходимое кол-во слотов,
            conflict_experiments - list, идентификаторы несовместных экспериментов.
            Пример: {'experiment_id': 'exp_16', 'count_slots': 3, 'conflict_experiments': ['exp_13']}
        return: List[dict], список экспериментов, которые не удалось разместить по слотам.
            Возвращает пустой список, если всем экспериментам хватило слотов.
        """
        self.experiments = sorted(experiments, key=lambda x: len(x['conflict_experiments']), reverse=True)
        self.slot_to_experiments = {slot: [] for slot in self.slots}
        self.experiment_to_slots = {pilot['experiment_id']: [] for pilot in self.experiments}
        
        self.overweight_experiments = []
        for exp in self.experiments:
            if exp['count_slots'] > len(self.slots):
                #print(f'ERROR: experiment_id={exp["experiment_id"]} needs too many slots.')
                self.overweight_experiments.append(exp)
                continue
            
            # найдём доступные слоты
            notavailable_slots = []
            for conflict_pilot_id in exp['conflict_experiments']:
                notavailable_slots += self.experiment_to_slots[conflict_pilot_id]
            available_slots = list(set(self.slots) - set(notavailable_slots))
            
            if exp['count_slots'] > len(available_slots):
                #print(f'ERROR: experiment_id="{exp["experiment_id"]}" not enough available slots.')
                self.overweight_experiments.append(exp)
                continue
            
            np.random.shuffle(available_slots)
            available_slots_orderby_count_pilot = sorted(
                available_slots,
                key=lambda x: len(self.slot_to_experiments[x]), reverse=True
            )
            
            pilot_slots = available_slots_orderby_count_pilot[:exp['count_slots']]
            self.experiment_to_slots[exp['experiment_id']] = list(pilot_slots) 
            
            for slot in pilot_slots:
                self.slot_to_experiments[slot].append(exp['experiment_id'])
            
        return self.overweight_experiments
        
    def process_user(self, user_id: str):
        """
        Определяет в какие эксперименты попадает пользователь.

        Сначала нужно определить слот пользователя.
        Затем для каждого эксперимента в этом слоте выбрать пилотную или контрольную группу.

        user_id - идентификатор пользователя.

        return - (int, List[tuple]), слот и список пар (experiment_id, pilot/control group).
            Example: (2, [('exp 3', 'pilot'), ('exp 5', 'control')]).
        """
        slot_modulo = len(self.slot_to_experiments)
        group_modulo = 2 #(0-pilot, 1-control)
        
        def get_hash_modulo(value: str, modulo: int, salt: str = '0'):
            """Вычисляем остаток от деления: (hash(value) + salt) % modulo."""
            hash_value = int(hashlib.md5(str.encode(str(value) + str(salt))).hexdigest(), 16)
            return hash_value % modulo
        
        user_slot = get_hash_modulo(user_id, modulo=slot_modulo, salt=self.salt_one)
        exp_and_group = []
        for exp in self.slot_to_experiments[user_slot]:
            group_hash = get_hash_modulo(user_id + exp, modulo=group_modulo, salt=self.salt_two)
            if group_hash == 1:
                group_name = 'pilot'
            else:
                group_name = 'control'
            exp_and_group.append(tuple([exp, group_name]))
        return (user_slot, exp_and_group)
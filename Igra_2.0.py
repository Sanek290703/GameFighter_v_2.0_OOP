import random
import time
from colorama import init, Fore, Back, Style


class Creature:
    number = -1

    def __init__(self, sword, shield, hil, money, hp, name, shop, bag=None):
        self.name = name
        self.shield = shield
        self.hp = hp
        self.sword = sword
        self.hil = hil
        self.money = money
        self.bag = bag if bag is not None else []
        self.max_hp = hp
        self.shop = shop
        Creature.number += 1
        self.my_number = Creature.number

    def info(self):
        print(f"\nName: {self.name}")
        print(f"HP: {self.hp}/{self.max_hp}")
        print(f"Sword: {self.sword}")
        print(f"Shield: {self.shield}")
        print(f"Hil: {self.hil}")
        print(f"Money: {self.money}")

    def attack(self, enemy):
        damage = random.randint(self.sword.min_hit, self.sword.max_hit)
        final_damage = enemy.defend(damage)
        if final_damage != 'reflect':
            enemy.hp -= final_damage
            return f"{self.name} нанес урон {final_damage}. У {enemy.name} осталось {enemy.hp} HP."
        else:
            ref_damage = self.defend(damage)
            self.hp -= ref_damage
            return f"{enemy.name} отразил {ref_damage}. У {self.name} осталось {self.hp} HP."

    def defend(self, damage):
        def_damage = damage - self.shield.protection
        def_damage = max(def_damage, 0)  # урон не может быть отрицательным
        return def_damage

    def loot(self, enemy):
        self.money += enemy.money
        print(f'{self.name} + {enemy.money} к кошельку')
        self.hp = self.hp + 65 if self.hp + 65 < self.max_hp else self.max_hp
        print(f'{self.name} восстановил здоровье (осталось {self.hp})')

        if enemy.sword.price != 0 and enemy.shield.price != 0:
            choice = random.choice([0, 0, 0, 0, 0, 1, 1, 2, 2, 3, 3])
            if choice == 1:
                self.bag.add(enemy.sword)
            elif choice == 2:
                self.bag.add(enemy.shield)
            elif choice == 3:
                self.bag.add(enemy.sword)
                self.bag.add(enemy.shield)
        elif enemy.sword.price != 0:
            if random.choice([0, 1, 1]) == 0:  # 1/3 шанс
                self.bag.add(enemy.sword)
        elif enemy.shield.price != 0:
            if random.choice([0, 1, 1]) == 0:  # 1/3 шанс
                self.bag.add(enemy.shield)

    def heal(self):
        if isinstance(self, Sworder) or isinstance(self, Defender):
            if self.hil > 0:
                self.hp += 45
                if self.hp > self.max_hp:
                    self.hp = self.max_hp
                self.hil -= 1
                print(f"{self.name} использовал зелье! У вас теперь {self.hp} HP.")
                return True
            print('Зелья закончились!')
            return False

        elif self.hp < 45 and self.hil > 0:
            self.hp += 55
            if self.hp > self.max_hp:
                self.hp = self.max_hp
            self.hil -= 1
            print(f"{self.name} использовал зелье! Теперь у него {self.hp} HP.")
            return True
        return False


class Sworder(Creature):
    def __init__(self, sword, shield, hil, money, hp, name, hit_chance_list, shop, bag=None):
        super().__init__(sword, shield, hil, money, hp, name, shop, bag)
        self.hit_chance_list = hit_chance_list

    def info(self):
        super().info()
        print(f"Шанс на двойной удар: {(sum(self.hit_chance_list) / len(self.hit_chance_list) - 1) * 100}%")

    def attack(self, enemy):
        hits = random.choice(self.hit_chance_list)
        if hits == 2:
            print('Двойной удар: ')
            for i in range(hits):
                print(f'{i + 1}.{super().attack(enemy)}')
        if hits == 1:
            print(f'{super().attack(enemy)}')


class Defender(Creature):
    def __init__(self, sword, shield, hil, money, hp, name, shop, reflect_chance, bag=[]):
        super().__init__(sword, shield, hil, money, hp, name, shop, bag)
        self.reflect_chance = reflect_chance

    def info(self):
        super().info()
        print(f"Шанс на отражение урона: {(sum(self.reflect_chance) / len(self.reflect_chance) - 1) * 100}%")

    def defend(self, incoming_damage):
        if random.choice(self.reflect_chance) == 2:
            print(f"{self.name} отразил весь урон!")
            return 'reflect'
        return super().defend(incoming_damage)


class Item:
    def __init__(self, name, price, atr):
        self.name = name
        self.price = price
        if len(atr) == 2:
            self.clas = 'sworder'
            self.min_hit, self.max_hit = atr
        elif len(atr) == 1:
            self.clas = 'defender'
            self.protection = atr[0]
        else:
            raise ValueError("Invalid attribute list for Item")

    def __str__(self):
        if self.clas == 'sworder':
            return f"{self.name} (Урон: {self.min_hit}-{self.max_hit}, Цена: {self.price})"
        else:
            return f"{self.name} (Защита: {self.protection}, Цена: {self.price})"


class Shop:
    def __init__(self, *items):
        self.items = list(items)

    def set_player(self, player):
        self.player = player

    def info(self):
        print(f"\nДоступные товары в магазине (Баланс {self.player.money}):", '-' * 15, sep='\n')
        for idx, item in enumerate(self.items, 1):
            print(f"{idx}.{item}")
        print(f'{len(self.items) + 1}.Зелье здоровья (+45) Цена: 4\n')
        print(f'{len(self.items) + 2}.В меню')
        choice = input("Выберите номер предмета (или 'В меню' для выхода): ")
        while not choice.isdigit() or not (1 <= int(choice) <= len(self.items) + 2):
            choice = input("Выберите номер предмета (или 'В меню' для выхода): ")
        self.remove_item(int(choice) - 1)

    # Метод для добавления новых товаров в магазин
    def add_item(self, item):
        self.items.append(item)

    # Метод для удаления товаров из магазина
    def remove_item(self, idx):
        if idx < len(self.items):
            if self.player.money >= self.items[idx].price:
                self.player.money -= self.items[idx].price
                print()
                self.player.bag.add(self.items.pop(idx))
                return self.info()
            else:
                print('Не хватает денег!')
                return self.info()
        elif idx == len(self.items):
            if self.player.money >= 4:
                self.player.money -= 4
                self.player.hil += 1
                print('\nВы купили зелье исцеления')
                return self.info()
            else:
                print('Не хватает денег!')
                return self.info()
        else:
            print('\nДо встречи в магазине!')


class Bag:
    def __init__(self):
        self.items = []
        self.player = None

    def set_player(self, player):
        self.player = player

    def add(self, item):
        if item.price != 0:
            self.items.append(item)
            print(f"Добавлено в сумку: {item}")
        return 0

    def info(self):
        print("\nВ сумке:", '-' * 15, sep='\n')
        if len(self.items) == 0:
            print('Ничего нет')
        else:
            for idx, item in enumerate(self.items, 1):
                print(f"{idx}.{item}")
            print(f'{len(self.items) + 1}.В меню')
            return self.take()

    def take(self):
        choice = input("Выберите номер предмета (или 'В меню' для выхода): ")
        while not choice.isdigit() or not (1 <= int(choice) <= len(self.items) + 1):
            choice = input("Выберите номер предмета (или 'В меню' для выхода): ")
        if 1 <= int(choice) <= len(self.items):
            item = self.items[int(choice) - 1]
            print('\n1.Надеть\n2.Продать\n3.Назад')
            choice = input(f"Что вы хотите сделать с {item}: ")
            while choice not in ['1', '2', '3']:
                choice = input(f"Что вы хотите сделать с {item}: ")
            if choice == '1':
                self.put_on(item)
                return self.info()
            elif choice == '2':
                self.sell(item)
                return self.info()
            elif choice == '3':
                return self.info()
        elif choice == len(self.items) + 1:
            print("Возвращаемся в меню...")

    def sell(self, item):
        shop_items = [shop_item.name for shop_item in self.player.shop.items]
        if item.name not in shop_items:
            self.player.shop.items.append(item)
        self.player.money += item.price
        print(f"Вы продали {item} за {item.price}.")
        self.items.remove(item)

    def put_on(self, item):
        if item.clas == 'defender':  # Если предмет является щитом
            if self.player.shield.price != 0:  # Проверка, чтобы не добавить "без щита" в сумку
                self.add(self.player.shield)
            self.player.shield = item
        elif item.clas == 'sworder':  # Если предмет является мечом
            if self.player.sword.price != 0:  # Проверка, чтобы не добавить "кулак" в сумку
                self.add(self.player.sword)
            self.player.sword = item
        print(f"{self.player.name} надел {item}.")
        self.items.remove(item)


class Battle:
    def __init__(self, player, enemy):
        self.player = player
        self.enemy = enemy

    def alive(self, creature):
        if creature.hp <= 0:
            creature.max_hp = 0
            print(f'{creature.name} погибает\n')
        return creature.hp > 0

    def player_turn(self, turn):
        print(f"\n1.Атаковать\n2.Восстановить здоровье (у вас {self.player.hil})")
        choice = input("Выберите действие: ")
        while choice not in ['1', '2']:
            choice = input("Выберите действие: ")
        print(f'Ход {turn}', '-' * 15, sep='\n')
        if choice == '1':
            self.enemy_turn()
            self.player.attack(self.enemy)
        elif choice == '2':
            self.enemy_turn()
            if not self.player.heal():
                print('Остается только бить...')
                self.player.attack(self.enemy)

    def enemy_turn(self):
        if not self.enemy.heal():
            print(self.enemy.attack(self.player))

    def start(self):
        self.enemy.info()
        turn = 1
        while self.alive(self.player) and self.alive(self.enemy):
            self.player_turn(turn)
            turn += 1
        if self.player.max_hp != 0:
            self.player.loot(self.enemy)


class Game:
    def __init__(self, name, character_class):
        # Мечи
        no_sw = Item("Кулаки", 0, (5, 13))  # минимальный урон 0, максимальный урон 15, цена 0
        sw1 = Item("Деревянный меч", 6, (10, 16))
        sw2 = Item("Каменный меч", 18, (15, 22))
        sw3 = Item("Бронзовый меч", 34, (20, 30))
        sw4 = Item("Золотой меч", 55, (28, 35))
        sw5 = Item("Железный меч", 84, (35, 46))
        sw6 = Item("Алмазный меч", 146, (50, 60))
        sw_prem = Item("Премиум меч", 1000, (55, 100))
        # Щиты
        no_sh = Item("Без щита", 0, (0,))  # минимальная защита 0, цена 0
        sh1 = Item("Деревянный щит", 9, (10,))
        sh2 = Item("Каменный щит", 20, (14,))
        sh3 = Item("Бронзовый щит", 37, (18,))
        sh4 = Item("Золотой щит", 64, (25,))
        sh5 = Item("Железный щит", 92, (31,))
        sh6 = Item("Алмазный щит", 110, (40,))
        sh_prem = Item("Премиум щит", 1000, (60,))

        self.swords = [no_sw, sw1, sw2, sw3, sw4, sw5, sw6, '']
        self.shields = [no_sh, sh1, sh2, sh3, sh4, sh5, sh6, '']
        self.hp = [9, 9, 10, 11, 11, 12, 14, 15, '']
        self.money = [2, 3, 3, 5, 7, 11, 14, 19, '']
        self.hil = [0, 0, 1, 1, 1, 2, 2, 3, '']

        chance = [1, 2]
        bag = Bag()
        if name == 'Sanek_29' and character_class == '1':
            print(f'\nС возвращением {name}, ваше высочество!')
            shop = Shop(no_sw, sw1, sw2, sw3, sw4, sw5, sw6, sw_prem)
            self.player = Sworder(sw_prem, sh_prem, 88, 10000, 290, name, chance, shop, bag)
        elif character_class == '1':
            shop = Shop(sw2, sw4, sw6, sw_prem, sh2, sh5, sh_prem)
            self.player = Sworder(sw1, no_sh, 8, 0, 120, name, chance, shop, bag)
        elif character_class == '2':
            shop = Shop(sw2, sw3, sw5, sw_prem, sh2, sh4, sh6, sh_prem)
            self.player = Defender(no_sw, sh1, 5, 0, 160, name, chance, shop, bag)
        shop.set_player(self.player)
        bag.set_player(self.player)
        # Создаем пустую сумку для игрока
        sw_boss = Item("Меч БОССА", 180, (44, 77))
        sh_boss = Item("Щит БОССА", 160, (44,))

        # Создаем босса (можно дополнительно определить параметры)
        self.boss = Creature(sw_boss, sh_boss, 8, 250, 222, "БОЛЬШОЙ И СТРАШНЫЙ БОСС", None, None)
        Creature.number -= 1
    def menu(self):
        print("\n--- Главное меню ---\n")
        print("1.Зайти в магазин")
        print("2.Атрибуты")
        print("3.Зайти в сумку")
        print("4.Начать битву")
        print("5.Посмотреть на босса")
        choice = input("Выберите действие: ")
        while choice not in ['1', '2', '3', '4', '5']:
            choice = input("Выберите действие: ")
        if choice == '1':
            self.player.shop.info()
            time.sleep(1)
            return self.menu()
        elif choice == '2':
            self.player.info()
            time.sleep(1)
            return self.menu()
        elif choice == '3':
            self.player.bag.info()
            time.sleep(1)
            return self.menu()
        elif choice == '4':
            battle = Battle(self.player, self.create_enimy())
            battle.start()
            if self.player.max_hp != 0:
                time.sleep(1)
                return self.menu()
            time.sleep(1)
            print('\n...Поражение...')
        elif choice == '5':
            self.boss.info()
            print('\n1.Готов!\n2.Пойду пожалуй подкачаюсь...')
            n = input('Готов? ')
            while n not in ['1', '2']:
                n = input('Готов? ')
            if n == '1':
                battle = Battle(self.player, self.boss)
                battle.start()
                if self.player.max_hp != 0:
                    print()
                    time.sleep(3)
                    lines = [
                        "Тень БОЛЬШОГО И СТРАШНОГО БОССА рассеялась благодаря твоему мужеству.",
                        "Твоя легенда останется в веках, а мой мир благодарит тебя за твою смелость.",
                        "Пусть звёзды осветят твой путь до следующего нашего встречения",
                        "Спасибо, что играл в мою игру",
                        "Увидимся!"]
                    print(
                        Fore.BLUE +
                        f"✨✨✨ Блеск звёзд нашего мира бледнеет перед твоим подвигом, {self.player.name}! ✨✨✨")
                    time.sleep(2)
                    for line in lines:
                        print(line)
                        time.sleep(2)
                    print(Fore.BLUE + "✨На просторах двоичного кода...✨")
                else:
                    print('\n...Поражение...')
            elif n == "2":
                time.sleep(1)
                return self.menu()

    def create_enimy(self):
        cycle = Creature.number // 8 if Creature.number // 8 < 5 else 5
        v_sw = random.choice(self.swords[cycle:cycle + 2])
        v_sh = random.choice(self.shields[cycle:cycle + 2])
        v_hp = random.choice(self.hp[cycle:cycle + 3]) * 10
        v_money = random.choice(self.money[cycle:cycle + 3])
        v_hil = random.choice(self.hil[cycle:cycle + 3])
        return Creature(v_sw, v_sh, v_hil, v_money, v_hp, f'Враг №{Creature.number + 1}', None, None)


init(autoreset=True)

print(Fore.BLUE + "🌌 ***Добро пожаловать в \"Тени Забытых Королевств\"!*** 🌌")
intro_lines = [
    "В этих древних землях, где мрак сплетается с светом, где герои рождаются из легенд,",
    "ты будешь стоять на стороне света или погрузишься в тьму? Сможешь ли ты пройти",
    "сквозь испытания, противостоять великим врагам и стать настоящим героем или правителем земель?",
    "🔥 *Возьми в руки свое оружие, выбери свой путь, и пусть судьба будет благосклонна к тебе на этом пути!* 🔥",
    "Приготовься к приключению, которое изменит твою жизнь!"]
time.sleep(1)
for line in intro_lines:
    print(line)
    time.sleep(1)
name = input(Fore.BLUE + "Как тебя зовут, путник? 🛡🗡 ")

print(f"Приветствую тебя в нашем лагере, {name}!")
print(Fore.BLUE + "🌌 ***Введу тебя в курс дела...*** 🌌")
intro_lines = [
    "В этом мире существует два класса, каждый из которых уникален и особенный:",
    "1. 🗡 **SWORDER** — мастер ближнего боя. Его мастерство меча поражает даже самых опытных воинов.",
    "Поговаривают, что благодаря своим навыкам он может ударить дважды за один ход!",
    "2. 🛡 **DEFENDER** — защитник и страж. Чей щит, как и его воля, абсолютно непоколебимы.",
    "Слухи гласят, что он может отразить весь урон, направленный на него, обратно врагу."]

for line in intro_lines:
    print(line)
    time.sleep(1)

clas = input(Fore.BLUE + "Каков твой выбор, путник? Кто ты — быстрый мастер меча или непробиваемый защитник? ")
while clas not in ['1', '2']:
    clas = input(Fore.BLUE + "Каков твой выбор, путник? Кто ты — быстрый мастер меча или непробиваемый защитник? ")

print("Отлично, отведу тебя к ним в гильдию!")
time.sleep(1)
game = Game(name, clas)
game.menu()

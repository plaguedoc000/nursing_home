import requests
import datetime
import random

BASE = "http://localhost:8000"


def get(path):
    return requests.get(f"{BASE}{path}").json()


def post(path, data):
    r = requests.post(f"{BASE}{path}", json=data)
    if not r.ok:
        print(f"  SKIP {path}: {r.json().get('detail', '')}")
        return None
    return r.json()


NAMES = [
    ("Иванов", "Иван", "Иванович"),
    ("Петров", "Пётр", "Алексеевич"),
    ("Сидорова", "Мария", "Николаевна"),
    ("Козлов", "Андрей", "Сергеевич"),
    ("Новикова", "Ольга", "Дмитриевна"),
    ("Морозов", "Сергей", "Васильевич"),
    ("Волкова", "Наталья", "Ивановна"),
    ("Алексеев", "Дмитрий", "Михайлович"),
    ("Лебедева", "Светлана", "Андреевна"),
    ("Семёнов", "Николай", "Петрович"),
    ("Егорова", "Галина", "Сергеевна"),
    ("Павлов", "Михаил", "Николаевич"),
    ("Громов", "Владимир", "Иванович"),
    ("Зайцева", "Татьяна", "Михайловна"),
    ("Борисов", "Александр", "Андреевич"),
    ("Кириллова", "Людмила", "Петровна"),
    ("Макаров", "Василий", "Дмитриевич"),
    ("Никитина", "Ирина", "Александровна"),
    ("Орлов", "Анатолий", "Васильевич"),
    ("Тихонова", "Валентина", "Николаевна"),
    ("Смирнов", "Алексей", "Сергеевич"),
    ("Кузнецова", "Елена", "Ивановна"),
    ("Попов", "Геннадий", "Петрович"),
    ("Соколова", "Нина", "Михайловна"),
    ("Михайлов", "Константин", "Андреевич"),
    ("Фёдорова", "Зинаида", "Васильевна"),
    ("Захаров", "Виктор", "Николаевич"),
    ("Белова", "Тамара", "Ивановна"),
    ("Комаров", "Леонид", "Петрович"),
    ("Степанова", "Вера", "Александровна"),
]


def rand_passport():
    series = str(random.randint(1000, 9999))
    number = str(random.randint(100000, 999999))
    return series, number


def rand_birth():
    year = random.randint(1930, 1960)
    month = random.randint(1, 12)
    day = random.randint(1, 28)
    return f"{year}-{month:02d}-{day:02d}"


today = datetime.date.today()

print("=== Пансионаты ===")
existing_p = get("/pansionats/")
print(f"  Уже есть: {len(existing_p)}")
for p in [
    {"name": "Пансионат Ромашка", "address": "г. Калуга, ул. Победы, 45"},
    {"name": "Пансионат Берёзка", "address": "г. Калуга, Берёзовая аллея, 12"},
]:
    r = post("/pansionats/", p)
    if r:
        print(f"  + {r['name']}")
all_p = get("/pansionats/")

print("\n=== Типы комнат ===")
for rt in [
    {"type_name": "VIP", "base_price": 3000.0},
    {"type_name": "Санаторный", "base_price": 5000.0},
    {"type_name": "Реабилитационный", "base_price": 4000.0},
]:
    r = post("/room-types/", rt)
    if r:
        print(f"  + {r['type_name']}")
all_rt = get("/room-types/")

print("\n=== Комнаты ===")
new_rooms = [
    (1, 1, "107"), (1, 2, "108"), (1, 3, "201"), (1, 1, "202"),
    (2, 2, "101"), (2, 3, "102"), (2, 1, "201"), (2, 4, "301"),
    (3, 3, "101"), (3, 5, "201"), (3, 1, "202"), (3, 2, "301"),
    (4, 4, "101"), (4, 5, "102"), (4, 1, "201"),
]
added = 0
for pi, rti, num in new_rooms:
    if pi <= len(all_p) and rti <= len(all_rt):
        r = post("/rooms/", {
            "pansionat_id": all_p[pi - 1]["pansionat_id"],
            "room_type_id": all_rt[rti - 1]["room_type_id"],
            "room_number": num,
        })
        if r:
            added += 1
print(f"  Добавлено: {added}")
all_rooms = get("/rooms/")

print("\n=== Кровати ===")
added_beds = 0
for room in all_rooms:
    beds_in_room = [b for b in get("/beds/") if b["room_id"] == room["room_id"]]
    for i in range(1, 4):
        label = f"Кровать {i}"
        if not any(b["bed_label"] == label for b in beds_in_room):
            r = post("/beds/", {"room_id": room["room_id"], "bed_label": label})
            if r:
                added_beds += 1
print(f"  Добавлено: {added_beds}")

print("\n=== Заселение жильцов ===")
all_beds = get("/beds/")
free_beds = [b for b in all_beds if b["is_active"] and b["current_resident_id"] is None]
random.shuffle(free_beds)
checked_in = []
names = random.sample(NAMES, min(35, len(free_beds), len(NAMES)))
for i, bed in enumerate(free_beds[:35]):
    if i >= len(names):
        break
    last, first, mid = names[i]
    ps, pn = rand_passport()
    checkout = today + datetime.timedelta(days=random.randint(5, 180))
    r = post("/residents/check-in", {
        "bed_id": bed["bed_id"],
        "last_name": last, "first_name": first, "middle_name": mid,
        "passport_series": ps, "passport_number": pn,
        "birth_date": rand_birth(),
        "planned_check_out": checkout.isoformat(),
    })
    if r:
        checked_in.append(r["record_id"])
print(f"  Заселено: {len(checked_in)}")

print("\n=== Выселение части ===")
archived = 0
for rid in checked_in[:10]:
    r = requests.post(f"{BASE}/residents/{rid}/check-out")
    if r.ok:
        archived += 1
print(f"  Выселено: {archived}")

print("\n=== Бронирования ===")
all_beds_fresh = get("/beds/")
free_for_booking = [b for b in all_beds_fresh if b["is_active"] and b["current_resident_id"] is None]
random.shuffle(free_for_booking)
booked = 0
for bed in free_for_booking[:10]:
    days_from = random.randint(5, 30)
    days_stay = random.randint(14, 60)
    checkin = today + datetime.timedelta(days=days_from)
    checkout = checkin + datetime.timedelta(days=days_stay)
    last, first, mid = random.choice(NAMES)
    phone = f"+7-9{random.randint(10, 99)}-{random.randint(100, 999)}-{random.randint(10, 99)}-{random.randint(10, 99)}"
    r = post("/bookings/", {
        "bed_id": bed["bed_id"],
        "future_res_last_name": last, "future_res_first_name": first, "future_res_mid_name": mid,
        "contact_phone": phone,
        "planned_check_in": checkin.isoformat(),
        "planned_check_out": checkout.isoformat(),
    })
    if r:
        booked += 1
print(f"  Создано бронирований: {booked}")

print("\n=== Итог ===")
print(f"  Пансионатов: {len(get('/pansionats/'))}")
print(f"  Типов комнат: {len(get('/room-types/'))}")
print(f"  Комнат: {len(get('/rooms/'))}")
print(f"  Кроватей: {len(get('/beds/'))}")
residents_all = get("/residents/")
curr = [r for r in residents_all if r["is_current"]]
arch = [r for r in residents_all if not r["is_current"]]
print(f"  Жильцов текущих: {len(curr)}, архив: {len(arch)}")
print(f"  Бронирований: {len(get('/bookings/'))}")

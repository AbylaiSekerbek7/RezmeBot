# venues.py
import json
import os
from typing import List, Dict, Optional

VENUES_FILE = "venues.json"

# стартовый набор заведений (если файла ещё нет)
DEFAULT_VENUES: List[Dict] = [
    {
        "id": 1,
        "category": "Кафе/Рестораны",
        "district": "Центр",
        "name": "Cafe Central",
        "address": "ул. Абая 10",
        "phone": "+7 777 123 45 67",
        "instagram": "https://instagram.com/cafecentral",
    },
    {
        "id": 2,
        "category": "Кафе/Рестораны",
        "district": "Левый берег",
        "name": "Sky Lounge",
        "address": "пр. Назарбаева 15",
        "phone": "+7 707 111 22 33",
        "instagram": "",
    },
    {
        "id": 3,
        "category": "Караоке",
        "district": "Центр",
        "name": "Karaoke Night",
        "address": "ул. Сатпаева 5",
        "phone": "+7 705 555 66 77",
        "instagram": "https://instagram.com/karaokenight",
    },
    {
        "id": 4,
        "category": "Боулинг",
        "district": "Правый берег",
        "name": "Strike Bowling",
        "address": "ТРЦ Mega, 3 этаж",
        "phone": "+7 700 999 88 77",
        "instagram": "",
    },
]


def _save_venues(venues: List[Dict]) -> None:
    with open(VENUES_FILE, "w", encoding="utf-8") as f:
        json.dump(venues, f, ensure_ascii=False, indent=2)


def _load_venues() -> List[Dict]:
    if not os.path.exists(VENUES_FILE):
        _save_venues(DEFAULT_VENUES)
        return DEFAULT_VENUES.copy()

    with open(VENUES_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    # на всякий случай гарантируем наличие всех ключей
    venues: List[Dict] = []
    for v in data:
        venues.append(
            {
                "id": v.get("id"),
                "name": v.get("name", "Без названия"),
                "category": v.get("category", "Не указано"),
                "district": v.get("district", "—"),
                "address": v.get("address", "—"),
                "phone": v.get("phone", "—"),
                "instagram": v.get("instagram", ""),
            }
        )
    return venues


def get_all_venues() -> List[Dict]:
    return _load_venues()


def get_venues_by_category(category: str) -> List[Dict]:
    venues = _load_venues()
    return [v for v in venues if v.get("category") == category]


def get_venues_by_district(district: str) -> List[Dict]:
    venues = _load_venues()
    return [v for v in venues if v.get("district") == district]


def get_districts() -> List[str]:
    venues = _load_venues()
    return sorted({v.get("district") for v in venues if v.get("district")})


def get_venue_by_id(venue_id: int) -> Optional[Dict]:
    venues = _load_venues()
    for v in venues:
        if v.get("id") == venue_id:
            return v
    return None


def add_venue(
    name: str,
    category: str,
    district: str,
    address: str,
    phone: str,
    instagram: str,
) -> Dict:
    venues = _load_venues()
    new_id = max((v.get("id", 0) for v in venues), default=0) + 1
    venue = {
        "id": new_id,
        "name": name,
        "category": category,
        "district": district,
        "address": address,
        "phone": phone,
        "instagram": instagram,
    }
    venues.append(venue)
    _save_venues(venues)
    return venue


def delete_venue(venue_id: int) -> bool:
    venues = _load_venues()
    new_venues = [v for v in venues if v.get("id") != venue_id]
    if len(new_venues) == len(venues):
        return False
    _save_venues(new_venues)
    return True

# venues.py
import json
import os
from typing import List, Dict, Optional

VENUES_FILE = "venues.json"

# стартовый набор заведений (если файла ещё нет)
DEFAULT_VENUES: List[Dict] = [
  {
    "id": 1,
    "name": "Hungry Rabbit",
    "category": "Ресторан, бар, боулинг, караоке",
    "district": "Правый берег",
    "address": "ул. Сакена Сейфулина 38",
    "phone": "+77019713777",
    "instagram": "https://www.instagram.com/hungryrabbit_jimmy?igsh=MTZndHdxeWZ3ZnFyeQ=="
  },
  {
    "id": 2,
    "name": "Jimmy",
    "category": "Караоке",
    "district": "Правый берег",
    "address": "ул. Сакена Сейфулина 38",
    "phone": "+77015222238",
    "instagram": ""
  },
  {
    "id": 3,
    "name": "Pasta La Vista",
    "category": "Кафе",
    "district": "Левый берег",
    "address": "ул. Акмешит 1",
    "phone": "+77776965696",
    "instagram": "https://www.instagram.com/pastalavista_astana?igsh=MTd0YTl5ZzIwZjBsNA=="
  },
  {
    "id": 4,
    "name": "Lou Lou",
    "category": "Ресторан",
    "district": "Центр",
    "address": "ул. Достык 13",
    "phone": "+77778081888",
    "instagram": "https://www.instagram.com/loulou_astana?igsh=MTR2Z2IzYmdzb2h6ZA=="
  },
  {
    "id": 5,
    "name": "Panno",
    "category": "Ресторан",
    "district": "Центр",
    "address": "ул. Достык 13",
    "phone": "+77079526090",
    "instagram": "https://www.instagram.com/panno.astana?igsh=MjJ2dzZ4aHB0eWg4"
  },
  {
    "id": 6,
    "name": "Underground",
    "category": "Play station клуб",
    "district": "Левый берег",
    "address": "ул. Санжара Асфендиярова 8",
    "phone": "+77084255099",
    "instagram": "https://www.instagram.com/underground_astana?igsh=MWRkNWl0Nmxocjd5Ng=="
  },
  {
    "id": 7,
    "name": "NextGen",
    "category": "Компьютерный клуб",
    "district": "Левый берег",
    "address": "ул. Бектуров 4",
    "phone": "+77476455620",
    "instagram": "https://www.instagram.com/nextgen.kz?igsh=MWZtcHdlcHdvMDN2eQ=="
  },
  {
    "id": 8,
    "name": "Sky",
    "category": "Лаундж-Бар",
    "district": "Центр",
    "address": "ул. Сыганак 45",
    "phone": "+77012021313",
    "instagram": "https://www.instagram.com/myata.sky?igsh=cGJlcHQ0c2F0bGNh"
  },
  {
    "id": 9,
    "name": "Pingwin Premium",
    "category": "Ресто-бар, караоке, боулинг",
    "district": "Правый берег",
    "address": "ул. Е 565, 3",
    "phone": "+77007205544",
    "instagram": "https://www.instagram.com/pingwin_premium?igsh=dmp3ZzFuNDM2c3Qz"
  },
  {
    "id": 10,
    "name": "Oblako",
    "category": "Лаундж-Бар",
    "district": "Центр",
    "address": "ул. Конаева 33",
    "phone": "+77761113663",
    "instagram": "https://www.instagram.com/oblako.astana?igsh=aTN3dWJnanhjYmdw"
  }
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

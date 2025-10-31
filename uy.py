# views.py
from datetime import datetime, date
from typing import Optional

from django.http import JsonResponse, HttpRequest
from django.views.decorators.http import require_http_methods

UZB_REGIONS = [
    "Andijon", "Buxoro", "Farg'ona", "Jizzax", "Xorazm", "Namangan",
    "Navoiy", "Qashqadaryo", "Samarqand", "Sirdaryo", "Surxondaryo",
    "Toshkent", "Toshkent shahri", "Qoraqalpog'iston" 
]


def _parse_age_from_request(request: HttpRequest) -> Optional[int]:
    """Try to get an integer age from request.POST or request.GET. Returns None if missing/invalid."""
    age = request.POST.get('age') if request.method == 'POST' else request.GET.get('age')
    if age:
        try:
            return int(age)
        except ValueError:
            return None

    birth = request.POST.get('birth_date') if request.method == 'POST' else request.GET.get('birth_date')
    if birth:
        try:
            b = datetime.strptime(birth, '%Y-%m-%d').date()
        except ValueError:
            return None
        today = date.today()
        years = today.year - b.year - ((today.month, today.day) < (b.month, b.day))
        return years

    return None


@require_http_methods(["GET", "POST"])
def check_age(request: HttpRequest):
    """View that checks whether the user is older than 18.

    Accepts either:
      - age (int) parameter, or
      - birth_date (YYYY-MM-DD)

    Returns JSON: { "valid": bool, "age": int|null, "message": str }
    """
    age = _parse_age_from_request(request)
    if age is None:
        return JsonResponse({
            'valid': False,
            'age': None,
            'message': "`age` yoki `birth_date` (YYYY-MM-DD) parametrlarini yuboring"
        }, status=400)

    is_over_18 = age >= 18
    return JsonResponse({
        'valid': is_over_18,
        'age': age,
        'message': "18 yoshdan katta" if is_over_18 else "18 yoshdan kichik"
    })


@require_http_methods(["GET", "POST"])
def regions(request: HttpRequest):
    """View that checks whether provided region is inside Uzbekistan.

    Accepts param `region` (string). Case-insensitive match against known list.
    Returns JSON: { "exists": bool, "region": str, "message": str }
    """
    region = request.POST.get('region') if request.method == 'POST' else request.GET.get('region')
    if not region:
        return JsonResponse({
            'exists': False,
            'region': None,
            'message': "`region` parametrini yuboring"
        }, status=400)

    normalized = region.strip().lower()
    matches = [r for r in UZB_REGIONS if r.lower() == normalized]
    exists = len(matches) > 0
    return JsonResponse({
        'exists': exists,
        'region': region,
        'message': "Viloyat O'zbekiston ichida mavjud" if exists else "Bunday viloyat topilmadi"
    })


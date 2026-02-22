import json
import requests
from datetime import datetime, time, timedelta
from ..static import ApiEndpoints


def extract_classes_ids(response: dict) -> tuple[bool, list[str]]:
    results = []

    data = response.get("data", {})
    items = data.get("items", [])

    pagination = data.get("pagination", {})
    is_last = pagination.get("isLast", False)

    for item in items:
        results.append(item.get("classId"))

    return is_last, results


def get_yesterday_and_four_years_ago():
    # Local timezone-aware "now"
    now = datetime.now().astimezone()

    # Yesterday's date (start of day)
    yesterday_date = now.date() - timedelta(days=1)
    yesterday_start = datetime.combine(yesterday_date, time.min).astimezone()

    # Date 4 years ago from yesterday (start of day)
    try:
        four_years_ago_date = yesterday_date.replace(year=yesterday_date.year - 4)
    except ValueError:
        # Fallback if yesterday was Feb 29 and the target year isn't a leap year
        four_years_ago_date = yesterday_date.replace(year=yesterday_date.year - 4, day=28)

    four_years_ago_start = datetime.combine(four_years_ago_date, time.min).astimezone()

    return {
        "yesterday_epoch_ms": int(yesterday_start.timestamp() * 1000),
        "yesterday_date": yesterday_date.strftime("%Y-%m-%d"),
        "four_years_ago_epoch_ms": int(four_years_ago_start.timestamp() * 1000),
        "four_years_ago_date": four_years_ago_date.strftime("%Y-%m-%d"),
    }


def get_classes(page_number: int, jwt_token: str):
    date_info = get_yesterday_and_four_years_ago()
    url = ApiEndpoints.GET_CLASSES(page_number)
    headers = ApiEndpoints.get_headers(jwt_token)

    payload = json.dumps({"classFilters":
      {"isFirstTsSelected": True,
       "courseId": None,
       "disciplineCodes": None,
       "seatAvailability": None,
       "langCode": None,
       "location": None,
       "classStatus": None,
       "isPrivate": None,
       "applyFilter": None,
       "applyTsFilter": None,
       "page": page_number,
       "pageNumber": page_number,
       "parentId": 18260,
       "size": 100,
       "instructorIds": [],
       "classStartDate": date_info.get("four_years_ago_epoch_ms"),
       "classEndDate": date_info.get("yesterday_epoch_ms"),
       "fromDate": date_info.get("four_years_ago_date"),
       "toDate": date_info.get("yesterday_date"),
       "selectedSort": "startDateTime",
       "sortOrder": "desc"
}})

    response = requests.post(url, headers=headers, data=payload)
    if response.status_code == 200:
        return extract_classes_ids(response.json())
    else:
        print(f"Failed to get classes on page {page_number}: {response.status_code}")
        return None, []

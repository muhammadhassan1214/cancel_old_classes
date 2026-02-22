import json
import requests
from ..static import ApiEndpoints


def cancel_class(class_id: str, jwt_token: str):
    url = ApiEndpoints.CANCEL_CLASS(class_id)
    headers = ApiEndpoints.get_headers(jwt_token)

    payload = json.dumps({
        "class": {
            "isCancelled": True
        }
    })

    response = requests.patch(url, headers=headers, data=payload)

    if response.status_code == 200:
        print(f"Class {class_id} cancelled successfully.")

    elif response.status_code == 400:
        try:
            response_data = response.json()
            # Safely navigate the nested JSON to find the error list
            errors = response_data.get("error", {}).get("errors", [])

            # Check if our specific "already cancelled" error code exists in the list
            is_already_cancelled = any(
                err.get("errorCode") == "class-management-service_2007"
                for err in errors
            )

            if is_already_cancelled:
                print(f"Class {class_id} is already cancelled. No action needed.")
            else:
                # If it's a 400 but a different error, print standard failure
                print(f"Failed to cancel class {class_id}: {response.status_code} - {response.text}")

        except ValueError:
            # Fallback just in case the API returns a 400 without a valid JSON body
            print(f"Failed to cancel class {class_id}: {response.status_code} - {response.text}")

    else:
        print(f"Failed to cancel class {class_id}: {response.status_code} - {response.text}")

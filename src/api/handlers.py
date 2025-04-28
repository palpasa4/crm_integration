import stat
from typing import Literal
import json, os, random, string, uuid
from datetime import datetime, timedelta
from src.core.middleware import *
from src.core.exceptions import *


def read_json(filename: str) -> dict:
    try:
        with open(filename, "r") as file:
            return json.load(file)
    except Exception as e:
        raise JSONException(message="Failed to read json!", status_code=500)


def write_json(data: dict, filename: str) -> None:
    try:
        with open(filename, "w") as file:
            json.dump(data, file, indent=4)
    except Exception as e:
        raise JSONException(message="Failed to write in json!", status_code=500)


def get_value_from_json(filename: str, crm: str, key: str) -> str | None:
    data = read_json(filename)
    if crm not in data or key not in data[crm]:
        raise ValueNotFoundException(
            message=f"{key} not found for CRM '{crm}'!", status_code=404
        )
    return data[crm][key]


def clear_json(filename: str) -> None:
    try:
        with open(filename, "w") as file:
            json.dump({}, file, indent=4)
    except Exception as e:
        raise JSONException(message="Error while clearing json!", status_code=500)


def generate_and_store_state(crm: str) -> str:
    filepath = "src/crmdata/state.json"
    state = "".join(random.choices(string.ascii_letters + string.digits, k=32))
    data = read_json(filepath) if os.path.exists(filepath) else {}
    data[crm] = {"state": state}
    write_json(data, filepath)
    return state


def check_state(crm: str, state: str) -> None:
    stored_state = get_value_from_json("src/crmdata/state.json", crm, "state")
    if state != stored_state:
        raise JSONException(
            message="Invalid state. Error processing request!", status_code=400
        )


def save_token_with_expiry(crm: str, token_data: dict) -> None:
    if not token_data.get("expires_in"):
        raise ValueNotFoundException(
            message="Expiry time not found in token response!", status_code=404
        )
    filepath = "src/crmdata/token.json"
    data = read_json(filepath) if os.path.exists(filepath) else {}
    issued_at = datetime.utcnow()
    expires_in = int(token_data["expires_in"])
    expires_at = issued_at + timedelta(seconds=expires_in)
    data[crm] = {
        **token_data,
        "issued_at": issued_at.isoformat(),
        "expires_at": expires_at.isoformat(),
    }
    write_json(data, filepath)


def valid_token(crm: str) -> bool:
    filepath = "src/crmdata/token.json"
    expiry_str = get_value_from_json(filepath, crm, "expires_at")
    if not expiry_str:
        raise JSONException(message="No expiry time found!", status_code=400)
    expiry_time = datetime.fromisoformat(expiry_str)
    current_time = datetime.utcnow()
    return True if current_time < expiry_time else False


def save_contacts(crm: str, contacts: dict) -> None:

    filepath = "src/crmdata/contacts.json"
    data = read_json(filepath) if os.path.exists(filepath) else {}
    if data.get(crm):
        raise ImportExistsException(
            message=f"Contacts have already been imported CRM: {crm}", status_code=409
        )
    data[crm] = contacts
    write_json(data, filepath)

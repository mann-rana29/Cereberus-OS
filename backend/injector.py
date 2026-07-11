## This is mock service to impersonate the original SCADA system

import requests
import time

BASE_URL="http://localhost:8000"

def register_permit():
    response = requests.post(f"{BASE_URL}/permit", json={
        "zone_id": "battery_4",
        "work_type": "HOT_WORK",
        "assigned_team": "Contractor Team B"
    })

    print(f"[PERMIT] {response.status_code} - {response.json()}")

def inject_co_spike():
    response = requests.post(f"{BASE_URL}/telemetry/event", json={
        "zone_id": "battery_4",
        "gas_type": "CO",
        "gas_ppm": 2.4
    })
    print(f"[TELEMETRY] {response.status_code} - {response.json()}")

if __name__ == "__main__":
    print("=== CERBERUS OS - DEMO INJECTOR ===")
    register_permit()
    time.sleep(2)
    inject_co_spike()


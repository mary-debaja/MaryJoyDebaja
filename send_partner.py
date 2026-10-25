
import requests

# ==========================================
# STEP 9 - SEND PRACTICE RECORD TO PARTNER
# ==========================================

partner_url = "https://abordaje-jm.onrender.com/api/students"

record = {
    "student_id": "EXT-002",
    "name": "Sample Exchange Record",
    "program": "BSIT",
    "year": 1,
    "section": "A",
    "source": "Partner API"
}

print("Sending practice record to partner...")
print("Partner URL:", partner_url)

try:
    response = requests.post(
        partner_url,
        json=record,
        timeout=30
    )

    print("\nStatus Code:", response.status_code)
    print("Response:", response.text)

    if response.status_code == 201:
        print("\nSUCCESS: Record sent to partner!")

    elif response.status_code == 409:
        print("\nStudent ID already exists in partner database.")

    elif response.status_code == 404:
        print("\nPartner POST endpoint was not found.")

    elif response.status_code == 405:
        print("\nPartner endpoint does not allow POST requests.")

    else:
        print("\nRequest was not accepted. Check response above.")

except requests.Timeout:
    print("\nERROR: Partner server took too long to respond.")

except requests.RequestException as error:
    print("\nERROR:", error)

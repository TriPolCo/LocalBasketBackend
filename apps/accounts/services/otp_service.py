# apps/accounts/services/otp_service.py
import random
import requests
from django.conf import settings
from django.core.cache import cache

FAST2SMS_API_KEY = "Iqelq9sAeCFlaLRwoFP9ScLGj4YTkK7SsdYXEvn7NDH5JueTdQpXnuU055YPLF0SZwRza0jl3cJPfMWN"
FAST2SMS_URL = "https://www.fast2sms.com/dev/bulkV2"


class OTPService:

    @staticmethod
    def clean_phone_number(phone: str) -> str:
        """Strips +91, spaces, and hyphens to get pure 10-digit number."""
        clean = "".join(filter(str.isdigit, str(phone)))
        if len(clean) > 10 and clean.startswith("91"):
            clean = clean[2:]
        return clean

    @classmethod
    def send_otp(cls, phone_number: str) -> dict:
        clean_phone = cls.clean_phone_number(phone_number)

        if len(clean_phone) != 10:
            return {
                "success": False,
                "message": "Please enter a valid 10-digit mobile number.",
            }

        # 1. Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))

        # 2. Store OTP in cache for 5 minutes (300 seconds)
        cache.set(f"otp_{clean_phone}", otp, timeout=300)

        # 🔑 Always print OTP in Django terminal for seamless local dev/testing
        print("\n" + "=" * 55)
        print(f"🔑 [OTP SERVICE] Mobile: {clean_phone} | Generated OTP: {otp}")
        print("=" * 55 + "\n")

        headers = {
            "authorization": FAST2SMS_API_KEY,
            "Content-Type": "application/json",
            "Cache-Control": "no-cache",
        }

        # 3. Normal SMS Route (Quick SMS 'q' route - bypasses DLT)
        quick_payload = {
            "route": "q",
            "message": f"Your DailyDrop verification OTP is {otp}. Valid for 5 minutes.",
            "language": "english",
            "flash": 0,
            "numbers": clean_phone,
        }

        try:
            response = requests.post(
                FAST2SMS_URL,
                json=quick_payload,
                headers=headers,
                timeout=10,
            )
            data = response.json()

            if data.get("return") is True:
                print(f"✅ Normal SMS Delivered: OTP {otp} sent to {clean_phone}")
                return {
                    "success": True,
                    "message": "OTP sent successfully to your mobile number via SMS.",
                }

            # Parse error message safely without slicing
            raw_msg = data.get("message")
            if isinstance(raw_msg, list):
                error_msg = ", ".join(str(m) for m in raw_msg)
            elif isinstance(raw_msg, str):
                error_msg = raw_msg
            else:
                error_msg = str(data)

            print(f"❌ Fast2SMS Response: {data}")

            # 🛠️ In DEBUG mode, don't block the mobile app if KYC is still pending
            if getattr(settings, "DEBUG", True):
                print(f"⚠️ [DEV MODE] Fast2SMS returned: {error_msg}")
                print(f"👉 Use console OTP: {otp} to test immediately.")
                return {
                    "success": True,
                    "message": f"OTP sent! (Dev Mode: {otp})",
                }

            return {"success": False, "message": error_msg}

        except Exception as e:
            print(f"❌ Fast2SMS Network Exception: {e}")
            if getattr(settings, "DEBUG", True):
                return {
                    "success": True,
                    "message": f"OTP sent! (Dev Mode: {otp})",
                }
            return {
                "success": False,
                "message": "SMS gateway error. Please try again later.",
            }

    @classmethod
    def verify_otp(cls, phone_number: str, entered_otp: str) -> bool:
        clean_phone = cls.clean_phone_number(phone_number)
        saved_otp = cache.get(f"otp_{clean_phone}")

        if saved_otp and str(saved_otp) == str(entered_otp).strip():
            cache.delete(f"otp_{clean_phone}")
            return True

        return False
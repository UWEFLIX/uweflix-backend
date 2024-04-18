import base64
import pyotp


class OTP:
    def __init__(self, key=pyotp.random_base32()):
        self._otp = pyotp.TOTP(key, interval=300)  # unique obj for server

    @staticmethod
    def string_to_base32(input_string) -> str:
        # Encode the input string to bytes
        input_bytes = input_string.encode('utf-8')

        # Use base64.b32encode with alternative encoding scheme 'base32hex'
        base32_bytes = base64.b32encode(input_bytes)

        # Convert bytes to string and decode to remove 'b' prefix
        base32_string = base32_bytes.decode('utf-8')

        return base32_string

    def generate(self, identifier: str) -> str:
        """
        Generate an otp that is unique to the user and this server
        :param identifier: Unique identifier of a user
        """
        key = OTP.string_to_base32(identifier)
        _otp = pyotp.TOTP(key, interval=300)  # unique obj for each user
        now = int(self._otp.now())  # the unique code for our server
        return _otp.at(now)  # unique code for our server AND user

    def verify(self, otp: str, identifier: str):
        """
        Verify an otp that is unique to the user and this server
        :param identifier: Unique identifier of a user
        :param otp: OTP to verify
        """
        key = OTP.string_to_base32(identifier)
        _otp = pyotp.TOTP(key, interval=300)  # unique obj for each user
        now = int(self._otp.now())  # the unique code for our server
        return _otp.verify(otp, now)  # verify


from sqlalchemy.util import await_only

from configurations.environments import Values as Config, Values
import aiohttp


class Otp:
    def __init__(self):
        self.request_link = Config.MSGWAY_API_URL
        self.api_key = Config.MSGWAY_API_KEY

    async def __send(self, mobile, code, template_id=None, params=None):
        headers = {
            "apiKey": self.api_key,
            "accept-language": "fa",
            "Content-Type": "application/json"
        }
        body = {
            "mobile": mobile,
            "method": "sms",
            'code': str(code),
            'params': params,
            'provider': Config.MSGWAY_PROVIDER if Config.MSGWAY_PROVIDER else None,
            "templateID": int(template_id) if template_id else Config.LOGIN_OTP_TEMPLATE_ID,
        }
        async with aiohttp.ClientSession() as session:
            async with session.post(self.request_link, json=body, headers=headers) as res:
                res = await res.json()
                return res

    async def send__login_code(self, mobile: str, code: int):
        return await self.__send(mobile, code)

    async def send_register_new_phone_code(self, mobile: str, code: int, ):
        return await self.__send(mobile, code, Values.NEW_PHONE_TEMPLATE_ID)

    async def send_change_phone_number_code(self, mobile: str, code: int, ):
        return await self.__send(mobile, code, Values.CHANGE_PHONE_TEMPLATE_ID)

    async def send_forget_password_code(self, mobile: str, code: int, user_name: str):
        return await self.__send(mobile, code, Values.FORGET_PASSWORD_TEMPLATE_ID, params=[user_name])

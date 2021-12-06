# flask_server
from flask import Flask, request, jsonify
from flask_restful import Resource, Api
from flask_cors import CORS

# telethon
from telethon import TelegramClient
from telethon import functions, types
# from telethon import TelegramClient, events, sync
from telethon.tl.functions.messages import GetHistoryRequest
import asyncio

loop = asyncio.get_event_loop()

api_id = 6852336
api_hash = '7b6b4a72ebb73ee2587c0dfbad693c66'

app = Flask('__name__')
api = Api(app)

CORS(app)

identitas = {}

class CreateSessionApi(Resource):
    def post(self):
        phone = request.form["phone"]

        async def main():
            global ph
            global resp
            try:
                client = TelegramClient('+{}'.format(phone), api_id, api_hash)
                await client.connect()

                me = await client.get_me()
                resp = me.is_self
                ph = me.phone

                # await client.log_out()
                await client.disconnect()

            except Exception as e:
                phone_code_hash = await client.send_code_request('+{}'.format(phone))
                resp = phone_code_hash.phone_code_hash
                await client.disconnect()

        loop.run_until_complete(main())
        if resp is True:
            return {
                "status": "{}".format(resp),
                "phone": "{}".format(ph)
                }
        else:
            return {"hash": "{}".format(resp)}

class InputCodeApi(Resource):
    def post(self):
        phone = request.form["phone"]
        code = request.form["code"]
        phone_code_hash = request.form["phone_code_hash"]

        async def main():
            global ph
            global resp
            try:
                client = TelegramClient('+{}'.format(phone), api_id, api_hash)
                await client.connect()

                await client.sign_in('+{}'.format(phone), code, phone_code_hash=phone_code_hash)
                me = await client.get_me()
                resp = me.is_self
                ph = me.phone

                # await client.log_out()
                await client.disconnect()

            except Exception as e:
                resp = e
                await client.disconnect()

        loop.run_until_complete(main())

        if resp is True:

            return {
                "status": "{}".format(resp),
                "phone": "{}".format(ph)
            }

        else:
            return {"error": "{}".format(resp)}

class LogOut(Resource):
    def post(self):
        phone = request.form["phone"]
        async def main():
            client = TelegramClient('+{}'.format(phone), api_id, api_hash)
            await client.connect()

            await client.log_out()
            await client.disconnect()

        loop.run_until_complete(main())

class GetPhoneId(Resource):
    def get(self):
        return identitas

    def post(self):
        _from = request.form["from"]
        phone = request.form["phone"]

        async def main(phone):
            # client = TelegramClient('+6283862243797', api_id, api_hash) # old
            client = TelegramClient(f'+{_from}', api_id, api_hash) # updated
            await client.connect()

            try:
                phoneId = await client(functions.users.GetUsersRequest(id=[phone]))
                phoneId_ = phoneId[0].id
                identitas["id"] = phoneId_
                global response
                response = {"status": "true"}

                await client.disconnect()
            except:
                identitas["id"] = ''
                response = {"status": "false"}

                await client.disconnect()

        loop.run_until_complete(main(phone))

        return response

class SendMessage(Resource):
    def post(self):
        _from = request.form["from"]
        _to = request.form["to"]
        message = request.form["message"]

        async def main():
            global resp
            try:
                client = TelegramClient('+{}'.format(_from), api_id, api_hash)
                await client.connect()
                await client.send_message(_to, '{}'.format(message))
                await client.disconnect()
                resp = True

            except Exception as e:
                await client.disconnect()
                resp = e

        loop.run_until_complete(main())
        if resp:
            return {"status": "{}".format(resp)}

class GetMessages(Resource):
    def post(self):
        _from = request.form["from"] # updated
        phone = request.form["to"] # updated
        limit = request.form["limit"]
        
        async def main():
            global posts
            # client = TelegramClient('+6283862243797', api_id, api_hash) #old
            client = TelegramClient(f'+{_from}', api_id, api_hash) # updated
            await client.connect()

            channel_username = phone
            channel_entity = await client.get_entity(channel_username)
            posts = await client(GetHistoryRequest(
                peer=channel_entity,
                limit=int(limit),
                offset_date=None,
                offset_id=0,
                max_id=0,
                min_id=0,
                add_offset=0,
                hash=0))
            
            await client.disconnect()

        loop.run_until_complete(main())

        d= posts.to_dict()['messages']
        return jsonify(d) # return jsonify(posts.to_dict())

api.add_resource(CreateSessionApi, "/auth", methods=["POST"]) # requestCode
api.add_resource(InputCodeApi, "/code", methods=["POST"]) # inputCode
api.add_resource(LogOut, "/logout", methods=["POST"]) # logout
api.add_resource(SendMessage, "/sendmsg", methods=["POST"]) # sendMessage
api.add_resource(GetPhoneId, "/getphoneid", methods=["GET", "POST"]) # getPhoneId
api.add_resource(GetMessages, "/getmessages", methods=["POST"]) # getMessages

if __name__ == "__main__":
    app.run(debug=True)

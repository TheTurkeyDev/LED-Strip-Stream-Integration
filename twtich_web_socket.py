import websockets
import json
import secret
import re
import data
from display_type import DisplayType


# Code referenced from https://github.com/SlackingVeteran/twitch-pubsub/blob/master/webSocketClient.py
class WebSocketClient:
    def __init__(self):
        # list of topics to subscribe to
        self.topics = ["channel-points-channel-v1.32907202"]
        self.auth_token = secret.auth_token
        pass

    async def connect(self):
        """
           Connecting to webSocket server
           websockets.client.connect returns a WebSocketClientProtocol, which is used to send and receive messages
        """
        print('Connecting...')
        self.connection = await websockets.client.connect('wss://ws.mjrlegends.com:2096')
        if self.connection.open:
            print('Connection established. Client correctly connected')
            json_message = json.dumps({
                "type": "LISTEN",
                "nonce": "snLwNF1kKeYxKOqHiq19%WEC*2UYuGxMrm6*30b9rFzKC0Yw5$S^2yXT!pyCLob8",
                "channel_id": '32907202',
                "topics": ["channel_points_reward_redeem"],
                "token": self.auth_token
            })
            await self.send_message(json_message)
            return self.connection

    async def send_message(self, message):
        """Sending message to webSocket server"""
        await self.connection.send(message)

    async def receive_message(self, connection):
        """Receiving all server messages and handling them"""
        while True:
            try:
                message = await connection.recv()
                msg_json = json.loads(message)
                if msg_json['type'] == "MESSAGE" and msg_json['topic'] == "channel_points_reward_redeem":
                    msg_data = msg_json['message']['redemption']
                    if msg_data['reward']['id'] == "c63fb418-8463-4a95-8fb5-04ffac7b964e":
                        usr_input = msg_data['user_input'].lower().strip()
                        if re.match(r"#[a-f0-9]{6}", usr_input):
                            usr_input = usr_input[1:]
                            rgb = tuple(int(usr_input[i:i + 2], 16) for i in (0, 2, 4))
                            data.display = DisplayType.SOLID
                            data.colors = [rgb]
                        elif usr_input.startswith('rainbow'):
                            data.display = DisplayType.RAINBOW
                        elif usr_input.startswith('colorblocks'):
                            data.display = DisplayType.BLOCK_COLOR
                            data.colors = []
                            pot_colors = usr_input.split(' ')
                            for col in pot_colors:
                                if re.match(r"#[a-f0-9]{6}", col):
                                    col = col[1:]
                                    rgb = tuple(int(col[i:i + 2], 16) for i in (0, 2, 4))
                                    data.colors.append(rgb)
                        elif usr_input.startswith('coloralternate'):
                            data.display = DisplayType.ALTERNATE_COLOR
                            data.colors = []
                            pot_colors = usr_input.split(' ')
                            for col in pot_colors:
                                if re.match(r"#[a-f0-9]{6}", col):
                                    col = col[1:]
                                    rgb = tuple(int(col[i:i + 2], 16) for i in (0, 2, 4))
                                    data.colors.append(rgb)

            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

import websockets
import json
import secret
import re
import data
from display_type import DisplayType

color_map = {
    'red': [0xFF, 0, 0],
    'blue': [0, 0, 0xFF],
    'green': [0, 0xFF, 0],
    'yellow': [0xFF, 0xFF, 0],
    'orange': [0xFF, 0xa5, 0],
    'pink': [0xFF, 0x14, 93],
    'purple': [0xFF, 0, 0xFF],
    'cyan': [0, 0xFF, 0xFF],
    'white': [0xFF, 0xFF, 0xFF],
    'black': [0, 0, 0]
}


# Code referenced from https://github.com/SlackingVeteran/twitch-pubsub/blob/master/webSocketClient.py
class WebSocketClient:
    def __init__(self):
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
                "nonce": "4jgUaUv0zdxBMe2tN6YSZaCROCwkO92baSaFzgT50sWFySI15ErkVpoIqfqLwoZ6",
                "channel_id": '32907202',
                "topics": ["channel_points_reward_redeem"],
                "token": self.auth_token
            })
            await self.send_message(json_message)
            return self.connection

    async def send_message(self, message):
        """Sending message to webSocket server"""
        await self.connection.send(message)

    def get_color_from_msg(self, msg):
        if msg in color_map.keys():
            return color_map[msg]
        else:
            if re.match(r"#[a-f0-9]{6}", msg):
                usr_input = msg[1:]
                return tuple(int(usr_input[i:i + 2], 16) for i in (0, 2, 4))
        return None

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
                        color = self.get_color_from_msg(usr_input)
                        if color is not None:
                            data.display = DisplayType.SOLID
                            data.colors = [color]
                        elif usr_input.startswith('rainbow'):
                            data.display = DisplayType.RAINBOW
                        elif usr_input.startswith('colorblocks'):
                            data.display = DisplayType.BLOCK_COLOR
                            data.colors = []
                            pot_colors = usr_input.split(' ')
                            for col in pot_colors:
                                color = self.get_color_from_msg(col)
                                if color is not None:
                                    data.colors.append(color)
                        elif usr_input.startswith('coloralternate'):
                            data.display = DisplayType.ALTERNATE_COLOR
                            data.colors = []
                            pot_colors = usr_input.split(' ')
                            for col in pot_colors:
                                color = self.get_color_from_msg(col)
                                if color is not None:
                                    data.colors.append(color)
                        elif usr_input.startswith('police'):
                            data.display = DisplayType.POLICE

            except websockets.exceptions.ConnectionClosed:
                print('Connection with server closed')
                break

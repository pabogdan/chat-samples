'''
Copyright 2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not
use this file except in compliance with the License.
A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an
"AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND,
either express or implied. See the License for the specific
language governing permissions and limitations under the License.
'''

import sys
import irc.bot
import requests


class TwitchBot(irc.bot.SingleServerIRCBot):
    def __init__(self, username, client_id, token, channel):
        self.client_id = client_id
        self.token = token
        self.channel = '#' + channel

        # Get the channel id, we will need this for v5 API calls
        url = 'https://api.twitch.tv/kraken/users?login=' + channel
        headers = {'Client-ID': client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
        r = requests.get(url, headers=headers).json()
        self.channel_id = r['users'][0]['_id']

        # Create IRC bot connection
        server = 'irc.chat.twitch.tv'
        port = 6667
        print('Connecting to ' + server + ' on port ' + str(port) + '...')
        print(irc.bot.SingleServerIRCBot.__init__(self, [(server, port, 'oauth:' + token)], username, username))

    def on_welcome(self, c, e):
        print('Joining ' + self.channel)
        print('PING', c.ping(self.channel))

        # You must request specific capabilities before you can use them
        c.cap('REQ', ':twitch.tv/membership')
        c.cap('REQ', ':twitch.tv/tags')
        c.cap('REQ', ':twitch.tv/commands')
        print("Join channel: ", c.join(self.channel))
        c.privmsg(self.channel, "Hello, fellow humans!")

    def on_pubmsg(self, server_connection, message):
        # If a chat message starts with an exclamation point, try to run it as a command
        if message.arguments[0][:1] == '!':
            cmd = message.arguments[0].split(' ')[0][1:]
            print('Received command: ' + cmd)
            self.do_command(message, cmd)
        return

    def do_command(self, message, cmd):
        c = self.connection
        # this should be display name
        msg_source = message.tags[3]['value']
        cmd = str.lower(cmd)
        # Poll the API to get current game.
        if cmd == "game":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' is currently playing ' + r['game'])

        # Poll the API the get the current status of the stream
        elif cmd == "title":
            url = 'https://api.twitch.tv/kraken/channels/' + self.channel_id
            headers = {'Client-ID': self.client_id, 'Accept': 'application/vnd.twitchtv.v5+json'}
            r = requests.get(url, headers=headers).json()
            c.privmsg(self.channel, r['display_name'] + ' channel title is currently ' + r['status'])
        # Provide basic information to viewers for specific commands
        elif cmd == "zap":
            message = "@" + msg_source + " zippity zapping @Awkar_."
            c.privmsg(self.channel, message)
        elif cmd == "beep":
            message = "@" + msg_source + " boop!"
            c.privmsg(self.channel, message)
        elif cmd == "twitter":
            c.privmsg(self.channel, "My twitter is @pabmcr")
        elif cmd == "github":
            c.privmsg(self.channel, "My github is https://github.com/pabogdan/")

        # The command was not recognized
        else:
            c.privmsg(self.channel, "Did not understand command: " + cmd)


def main():
    if len(sys.argv) != 5:
        print("Usage: twitchbot <username> <client id> <token> <channel>")
        sys.exit(1)

    username = sys.argv[1]
    client_id = sys.argv[2]
    token = sys.argv[3]
    channel = sys.argv[4]

    bot = TwitchBot(username, client_id, token, channel)
    bot.start()


if __name__ == "__main__":
    main()

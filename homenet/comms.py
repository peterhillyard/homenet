import json as json
import zmq as zmq

from base import SettingsConfig


class Comms:

    def __init__(self, sys_settings_fname):
        self.init_pub_sub(sys_settings_fname)

    def init_pub_sub(self, sys_settings_fname):
        sc = SettingsConfig(sys_settings_fname)
        pub_facing_endpoint = sc.get_pub_facing_endpoint()
        sub_facing_endpoint = sc.get_sub_facing_endpoint()

        self.context = zmq.Context()

        self.sub_facing_socket = self.context.socket(zmq.SUB)
        self.sub_facing_socket.connect(sub_facing_endpoint)
        self.sub_facing_socket.setsockopt(zmq.LINGER, 0)
        # self.sub_facing_socket.subscribe('')

        self.pub_facing_socket = self.context.socket(zmq.PUB)
        self.pub_facing_socket.connect(pub_facing_endpoint)

    def set_subscriptions(self, sub_list):
        for sub_str in sub_list:
            self.sub_facing_socket.subscribe(sub_str)

    def close_pub_sub(self):
        self.sub_facing_socket.close()
        self.pub_facing_socket.close()
        self.context.term()

    def send_msg(self, msg_type, payload):
        self.pub_facing_socket.send_multipart(
            [msg_type.encode('utf-8'), json.dumps(payload).encode('utf-8')]
        )

    def recv_msg(self):
        try:
            msg = self.sub_facing_socket.recv_multipart(flags=zmq.NOBLOCK)
        except zmq.ZMQError:
            msg = None

        return msg


class CommsForwarder:

    def __init__(self, sys_settings_fname):
        self.setup_forwarder(sys_settings_fname)

    def setup_forwarder(self, sys_settings_fname):
        sc = SettingsConfig(sys_settings_fname)
        pub_facing_endpoint = sc.get_pub_facing_endpoint()
        sub_facing_endpoint = sc.get_sub_facing_endpoint()

        self.context = zmq.Context()

        self.frontend = self.context.socket(zmq.SUB)
        self.frontend.bind(pub_facing_endpoint)
        self.frontend.setsockopt(zmq.LINGER, 0)
        self.frontend.subscribe('')

        # Socket facing publishers
        self.backend = self.context.socket(zmq.PUB)
        self.backend.bind(sub_facing_endpoint)

    def start_forwarding(self):
        try:
            print("Forwarder successfully started")
            zmq.device(zmq.FORWARDER, self.frontend, self.backend)
        except (Exception, KeyboardInterrupt):
            # print(e)
            print("bringing down zmq device")
        finally:
            self.frontend.close()
            self.backend.close()
            self.context.term()


if __name__ == "__main__":
    sys_settings_fname = 'sys_settings.json'
    cf = CommsForwarder(sys_settings_fname)

    cf.start_forwarding()

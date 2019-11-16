import comms as comms
import json as json
import uuid as uuid
import time as time
import datetime as datetime


class DeviceTable:

    def __init__(self, sys_settings_fname, device_table_fname):
        self.device_table_fname = device_table_fname
        self.sub_list = [b'new_arp_pkt']
        self.comms = comms.Comms(sys_settings_fname)
        self.comms.set_subscriptions(self.sub_list)

        self.device_list = load_device_table(device_table_fname)
        self.device_lut = update_device_lut(self.device_list)

    def run_device_table_routine(self):
        msg = self.comms.recv_msg()
        if msg:
            self.process_message(msg)

        time.sleep(0.1)

    def process_message(self, msg):
        payload = json.loads(msg[1].decode('utf-8'))

        src_mac = payload['sender_mac_as_str_with_colons']
        src_ip = payload['sender_ip_as_str_with_dots']

        pub_new_table_flag = False
        utc_now = datetime.datetime.utcnow()
        if src_mac in self.device_lut.keys():
            dev_ip = self.device_lut[src_mac]['ip']
            if dev_ip != src_ip:
                pub_new_table_flag = True
                self.device_lut[src_mac]['ip'] = src_ip
            self.device_lut[src_mac]['last_seen'] = \
                utc_now.isoformat() + '+00:00'
        else:
            new_device = {
                'id': str(uuid.uuid4()),
                'mac': src_mac,
                'ip': src_ip,
                'alias': '',
                'last_seen': utc_now.isoformat() + '+00:00'
            }
            self.device_list.append(new_device)
            self.device_lut = update_device_lut(self.device_list)
            pub_new_table_flag = True

        # TODO: save data to database
        save_device_table(self.device_table_fname, self.device_list)

        if pub_new_table_flag:
            self.comms.send_msg('new_table', self.device_list)
            # TODO: publish new table

    def clean_up(self):
        self.comms.close_pub_sub()


def load_device_table(device_table_fname):
    # TODO: Load from db
    with open(device_table_fname, 'r') as f:
        tmp_dict = json.load(f)
    return tmp_dict['devices']


def save_device_table(device_table_fname, device_list):
    with open(device_table_fname, 'w') as f:
        out_dict = {
            'devices': device_list
        }
        json.dump(out_dict, f, indent=2)


def update_device_lut(device_list):
    device_lut = {
        dev['mac']: dev for dev in device_list
    }
    return device_lut


def main():
    mt = DeviceTable('sys_settings.json', 'device_table.json')

    is_running = True
    while is_running:
        try:
            mt.run_device_table_routine()
        except KeyboardInterrupt:
            is_running = False
            mt.clean_up()


if __name__ == '__main__':
    main()

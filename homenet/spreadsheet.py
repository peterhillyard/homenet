import gspread as gs
from oauth2client.service_account import ServiceAccountCredentials
import datetime as datetime
import comms as comms
import time as time
import json as json
import uuid as uuid


class GSDatabaseInterface:

    def __init__(self, sys_settings_fname, gs_settings_fname):
        self.sub_list = [b'new_arp_pkt', b'new_table']
        self.comms = comms.Comms(sys_settings_fname)
        self.comms.set_subscriptions(self.sub_list)

        self.gs_settings_fname = gs_settings_fname
        self.load_sys_settings(gs_settings_fname)
        self.open_client(gs_settings_fname)
        self.create_database()
        self.open_spreadsheet()
        self.open_worksheets()

        self.arp_data_list = []
        self.last_arp_data_dump = 0

    def load_sys_settings(self, gs_settings_fname):
        with open(gs_settings_fname, 'r') as f:
            self.settings_dict = json.load(f)

    def open_client(self, gs_settings_fname):
        cred_fname = self.settings_dict['gspread_cred_fname']

        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            cred_fname,
            scope
        )

        self.client = gs.authorize(creds)

    def create_database(self):
        try:
            tmp = self.client.open_by_key(self.settings_dict['gspread_id'])
            tmp.title
            return
        except Exception:
            pass

        # Create the new spreadsheet, save the id
        sheet = self.client.create('homenet')
        self.settings_dict['gspread_id'] = sheet.id

        # Give permission to users
        for share_obj in self.settings_dict['gspread_sharing_list']:
            if share_obj['perm_type'] == 'user' and \
               share_obj['role'] in ['reader', 'writer']:
                sheet.share(
                    share_obj['email'],
                    perm_type=share_obj['perm_type'],
                    role=share_obj['role']
                )

        # Set up worksheets
        for ii, ws_meta in enumerate(self.settings_dict['gspread_worksheets']):
            ws = sheet.add_worksheet(
                ws_meta['title'],
                2,
                len(ws_meta['header'])
            )

            ws.insert_row(ws_meta['header'])
            self.settings_dict['gspread_worksheets'][ii]['index'] = ws.id

        # Update the system settings
        with open(self.gs_settings_fname, 'w') as f:
            json.dump(self.settings_dict, f, indent=2)

    def open_spreadsheet(self):
        id = self.settings_dict['gspread_id']
        self.sheet = self.client.open_by_key(id)

    def open_worksheets(self):
        self.worksheet_lut = {}
        for ws_meta in self.settings_dict['gspread_worksheets']:
            self.worksheet_lut[ws_meta['title']] = ws_meta
            if ws_meta['title'] == 'devices':
                self.devices_ws = self.sheet.worksheet(ws_meta['title'])
            if ws_meta['title'] == 'arps':
                self.arps_ws = self.sheet.worksheet(ws_meta['title'])

    def update_devices(self, device_obj_list):
        values = []
        key_list = self.worksheet_lut['devices']['header']
        for device_obj in device_obj_list:
            values.append([device_obj[key] for key in key_list])

        try:
            self.sheet.values_clear('devices!A2:D')
            self.sheet.values_update(
                'devices!A2:D',
                params={
                    'valueInputOption': 'USER_ENTERED'
                },
                body={
                    'values': values
                }
            )
        except Exception:
            raise ValueError

    def append_to_arps_data(self, arp_data):
        now = datetime.datetime.now()
        datetime_str = now.isoformat()
        uid = str(uuid.uuid4())
        values = [
            uid,
            arp_data['sender_mac_as_str_with_colons'],
            arp_data['sender_ip_as_str_with_dots'],
            arp_data['target_mac_as_str_with_colons'],
            arp_data['target_ip_as_str_with_dots'],
            datetime_str,
        ]
        self.arp_data_list.append(values)

    def update_arps_data(self):

        if not self.arp_data_list:
            return

        r = 'arps!A2:F'

        q_params = {
            'insertDataOption': 'INSERT_ROWS',
            'valueInputOption': 'RAW'
        }

        body = {
            'range': r,
            'majorDimension': 'ROWS',
            'values': self.arp_data_list
        }

        try:
            if False:
                self.sheet.values_append(range=r, params=q_params, body=body)
            self.arp_data_list = []
        except Exception:
            raise ValueError

    def del_all_spreadsheets(self):
        sp_files = self.client.list_spreadsheet_files()
        for s in sp_files:
            print(s['id'])
            try:
                self.client.del_spreadsheet(s['id'])
            except Exception:
                pass

    def run_database_interface_routine(self):
        msg = self.comms.recv_msg()
        if not msg:
            time.sleep(0.1)
            return

        if msg[0] == b'new_arp_pkt':
            arp_data = json.loads(msg[1].decode('utf-8'))
            self.append_to_arps_data(arp_data)
            if time.time() - self.last_arp_data_dump > 2.0:
                try:
                    self.update_arps_data()
                    self.last_arp_data_dump = time.time()
                except ValueError:
                    raise ValueError

        if msg[0] == b'new_table':
            device_list = json.loads(msg[1].decode('utf-8'))
            try:
                self.update_devices(device_list)
            except ValueError:
                raise ValueError


if __name__ == '__main__':
    gsdi = GSDatabaseInterface('sys_settings.json', 'gspread_settings.json')

    is_running = True
    print('starting database interface...')
    while is_running:
        try:
            gsdi.run_database_interface_routine()
        except KeyboardInterrupt:
            is_running = False
            print('Closing up')
        except ValueError:
            print('re-creating database interface')
            gsdi = GSDatabaseInterface(
                'sys_settings.json',
                'gspread_settings.json'
            )

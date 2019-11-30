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
        self.load_gs_settings(gs_settings_fname)

        self.open_client(gs_settings_fname)
        self.initialize_device_database()
        self.initialize_arp_database()

        self.arp_data_list = []
        self.last_arp_data_dump = 0

    def load_gs_settings(self, gs_settings_fname):
        with open(gs_settings_fname, 'r') as f:
            self.gs_settings = json.load(f)

    def open_client(self, gs_settings_fname):
        cred_fname = self.gs_settings['gspread_cred_fname']

        scope = [
            'https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive'
        ]

        creds = ServiceAccountCredentials.from_json_keyfile_name(
            cred_fname,
            scope
        )

        self.client = gs.authorize(creds)

    def set_permissions(self, sheet):
        # Give permission to users
        for share_obj in self.gs_settings['gspread_sharing_list']:
            if share_obj['perm_type'] == 'user' and \
               share_obj['role'] in ['reader', 'writer']:
                sheet.share(
                    share_obj['email'],
                    perm_type=share_obj['perm_type'],
                    role=share_obj['role'],
                    notify=share_obj['notify']
                )

    def initialize_device_database(self):
        title = self.gs_settings['devices_spreadsheet']['title']
        new_ss_created = False
        try:
            self.device_ss = self.client.open(title)
        except gs.exceptions.SpreadsheetNotFound:
            self.device_ss = self.client.create(title)
            new_ss_created = True

        self.gs_settings['devices_spreadsheet']['key'] = self.device_ss.id

        ws_obj_list = self.gs_settings['devices_spreadsheet']['worksheets']
        self.device_ss_worksheet_lut = {}
        for ii, ws_meta in enumerate(ws_obj_list):
            if new_ss_created and ws_meta['title'] == 'devices':
                ws = self.device_ss.sheet1
                ws.update_title(ws_meta['title'])
                ws.resize(rows=1, cols=len(ws_meta['header']))
                ws.insert_row(ws_meta['header'])
            elif new_ss_created and ws_meta['title'] == 'stats':
                ws = self.device_ss.add_worksheet(
                    ws_meta['title'],
                    1,
                    len(ws_meta['header'])
                )
                ws.insert_row(ws_meta['header'])
                self.create_device_stats_ws(ws)
            else:
                ws = self.device_ss.worksheet(ws_meta['title'])

            self.device_ss_worksheet_lut[ws_meta['title']] = {
                'ws': ws,
                'meta': ws_meta
            }
            self.gs_settings['devices_spreadsheet']['worksheets'][ii]['index'] = ws.id

        if new_ss_created:
            self.set_permissions(self.device_ss)
            self.update_gs_setttings()

    def initialize_arp_database(self):
        title_pre = self.gs_settings['arp_pkt_spreadsheet']['title_prefix']
        ymd_str = datetime.datetime.now().strftime('%Y_%m_%d')
        self.arp_ss_title = title_pre + ymd_str
        new_ss_created = False
        try:
            self.arp_ss = self.client.open(self.arp_ss_title)
        except gs.SpreadsheetNotFound:
            self.arp_ss = self.client.create(self.arp_ss_title)
            new_ss_created = True

        self.gs_settings['arp_pkt_spreadsheet']['key'] = self.arp_ss.id

        ws_obj_list = self.gs_settings['arp_pkt_spreadsheet']['worksheets']
        self.arp_ss_worksheet_lut = {}
        for ii, ws_meta in enumerate(ws_obj_list):
            if new_ss_created and ii == 0:
                ws = self.arp_ss.sheet1
                ws.update_title(ws_meta['title'])
                ws.resize(rows=1, cols=len(ws_meta['header']))
                ws.insert_row(ws_meta['header'])
            elif new_ss_created and ii != 0:
                ws = self.arp_ss.add_worksheet(
                    ws_meta['title'],
                    1,
                    len(ws_meta['header'])
                )
                ws.insert_row(ws_meta['header'])
            else:
                ws = self.arp_ss.worksheet(ws_meta['title'])

            self.arp_ss_worksheet_lut[ws_meta['title']] = {
                'ws': ws,
                'meta': ws_meta
            }
            self.gs_settings['arp_pkt_spreadsheet']['worksheets'][ii]['index'] = ws.id

        if new_ss_created:
            self.set_permissions(self.arp_ss)
            self.update_gs_setttings()

    def update_gs_setttings(self):
        # Update the system settings
        with open(self.gs_settings_fname, 'w') as f:
            json.dump(self.gs_settings, f, indent=2)

    def update_devices(self, device_obj_list):
        values = []
        key_list = self.device_ss_worksheet_lut['devices']['meta']['header']
        for device_obj in device_obj_list:
            values.append([device_obj[key] for key in key_list])

        try:
            self.device_ss.values_clear('devices!A2:D')
            self.device_ss.values_update(
                'devices!A2:D',
                params={
                    'valueInputOption': 'USER_ENTERED'
                },
                body={
                    'values': values
                }
            )
        except Exception:
            print('failed to update devices')
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
            self.arp_ss.values_append(range=r, params=q_params, body=body)
            self.arp_data_list = []
        except Exception as err:
            print('failed to update arps. {}'.format(err))
            raise ValueError

    def update_device_stats_col(self, ws, col_letter, val_str_list):
        # Lookup IP address
        time.sleep(3)
        cell_list = ws.range('{}2:{}257'.format(col_letter, col_letter))

        for ii, cell in enumerate(cell_list):
            val_str = ''
            for a_str in val_str_list:
                val_str += a_str.format(cell.row)

            cell.value = val_str

        ws.update_cells(cell_list, value_input_option='USER_ENTERED')

    def create_device_stats_ws(self, ws):
        ws.update_acell('A2', '=unique(devices!$B$2:B)')
        ws.update_acell('J2', '=now()')

        # Lookup IP address
        val_str_list = ['=VLOOKUP(A{},devices!$B$2:$D,2,FALSE)']
        self.update_device_stats_col(ws, 'B', val_str_list)

        # Lookup last_seen address
        val_str_list = ['=VLOOKUP(A{},devices!$B$2:$D,3,FALSE)']
        self.update_device_stats_col(ws, 'D', val_str_list)

        # Update last seen as datetime
        val_str_list = [
            '=DATEVALUE(MID(D{},1,10))',
            ' + TIMEVALUE(MID(D{},12,8))'
        ]
        self.update_device_stats_col(ws, 'E', val_str_list)

        # Update days since last seen
        val_str_list = ['=DAYS($J$2,E{})']
        self.update_device_stats_col(ws, 'F', val_str_list)

        # Update hours since last seen
        val_str_list = ['=FLOOR(($J$2-E{})*24)']
        self.update_device_stats_col(ws, 'G', val_str_list)

        # Update minutes since last seen
        val_str_list = ['=FLOOR(($J$2-E{})*24*60)']
        self.update_device_stats_col(ws, 'H', val_str_list)

        # Update seconds since last seen
        val_str_list = ['=FLOOR(($J$2-E{})*24*60*60)']
        self.update_device_stats_col(ws, 'I', val_str_list)

    def run_database_interface_routine(self):
        msg = self.comms.recv_msg()
        if not msg:
            time.sleep(0.1)
            return

        if msg[0] == b'new_arp_pkt':
            arp_data = json.loads(msg[1].decode('utf-8'))

            now = datetime.datetime.now()
            ymd_str = now.strftime("%Y_%m_%d")
            if ymd_str not in self.arp_ss_title:
                # send off any data in the list
                try:
                    self.update_arps_data()
                    self.last_arp_data_dump = time.time()
                except ValueError:
                    raise ValueError

                # it's a new day. create new spreadsheet
                self.initialize_arp_database()

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

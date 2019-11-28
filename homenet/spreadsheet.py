import gspread as gs
from oauth2client.service_account import ServiceAccountCredentials
import json as json


class GSDatabaseInterface:

    def __init__(self, gs_settings_fname):
        self.gs_settings_fname = gs_settings_fname
        self.load_sys_settings(gs_settings_fname)
        self.open_client(gs_settings_fname)
        self.create_database()
        self.open_spreadsheet()
        self.open_worksheets()

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
        for ws_meta in self.settings_dict['gspread_worksheets']:
            if ws_meta['title'] == 'devices':
                self.devices_ws = self.sheet.get_worksheet(ws_meta['index'])
            if ws_meta['title'] == 'arps':
                self.arps_ws = self.sheet.get_worksheet(ws_meta['index'])

    def update_devices(self, device_obj_list):
        self.devices_ws.clear()
        # for device_obj in device_obj_list:

    def del_all_spreadsheets(self):
        sp_files = self.client.list_spreadsheet_files()
        for s in sp_files:
            print(s['id'])
            try:
                self.client.del_spreadsheet(s['id'])
            except Exception:
                pass




if __name__ == '__main__':
    gsd = GSDatabaseInterface('gspread_settings.json')

    # gsd.del_all_spreadsheets()
    # gsd.create_database()
    # gsd.update_devices([])

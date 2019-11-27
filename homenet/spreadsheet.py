import gspread as gs
from oauth2client.service_account import ServiceAccountCredentials
import json as json


class GSDatabaseInterface:

    def __init__(self, gs_settings_fname):
        self.gs_settings_fname = gs_settings_fname
        self.load_sys_settings(gs_settings_fname)
        self.open_client(gs_settings_fname)

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

    def is_database_created(self):
        return self.settings_dict['gspread_id'] != ''

    def create_database(self):
        if self.is_database_created():
            return

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
        for ii, ws in enumerate(self.settings_dict['gspread_worksheets']):
            ws = sheet.add_worksheet(
                ws['title'],
                2,
                len(ws['header'])
            )

            ws.insert_row(ws['header'])
            self.settings_dict['gspread_worksheets'][ii]['index'] = ws.id

        # Update the system settings
        with open(self.gs_settings_fname, 'w') as f:
            json.dump(self.settings_dict, f, indent=2)

    def open_spreadsheet(self):
        id = self.settings_dict['gspread_id']
        self.sheet = self.client.open_by_key(id)

    def del_all_spreadsheets(self):
        sp_files = self.client.list_spreadsheet_files()
        for s in sp_files:
            self.client.del_spreadsheet(s['id'])


if __name__ == '__main__':
    gsd = GSDatabaseInterface('gspread_settings.json')

    gsd.del_all_spreadsheets()
    gsd.create_database()

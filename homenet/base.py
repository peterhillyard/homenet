import json as json


class SettingsConfig:

    def __init__(self, sys_settings_fname):
        self.load_settings(sys_settings_fname)

    def load_settings(self, sys_settings_fname):
        with open(sys_settings_fname, 'r') as f:
            self.cfg_dict = json.load(f)

    def get_interface(self):
        return self.cfg_dict['interface_name']

    def get_sub_facing_endpoint(self):
        return self.cfg_dict['sub_facing_endpoint']

    def get_pub_facing_endpoint(self):
        return self.cfg_dict['pub_facing_endpoint']

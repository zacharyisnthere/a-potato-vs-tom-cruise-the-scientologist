#!/home/zachary/Documents/Repos/apotatovstomcruisethescientologist/venv/bin/python

import json

class SettingsManager():
    def __init__(self):
        self.settings = self.get_settings()

    def save_settings(self, data):
        with open('./memory/settings.mem', 'w') as data_file:
            json.dump(data, data_file)

        self.settings = self.get_settings()

    def get_settings(self):
        with open('./memory/settings.mem') as data_file:
            data = json.load(data_file)
        return data

    def reset_settings(self):
        default_master_volume = 60
        default_music_volume = 60
        default_sfx_volume = 60

        self.settings['master_volume'] = default_master_volume
        self.settings['music_volume'] = default_music_volume
        self.settings['sfx_volume'] = default_sfx_volume

        self.save_settings(self.settings)

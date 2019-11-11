#!/usr/bin/env python
# -*- coding: utf-8 -*-
import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk
import configparser
import http.client


class UI(object):

    def __init__(self, parent=None, context=None):

        if not context:
            context = {}
        # ----- Class informations
        self.is_main = True
        self.is_modal = False
        self._maximize = False
        self.parent = parent
        self.user = False if not parent else self.parent.user
        self.interface = self.__class__.__name__.lower()
        self.builder = Gtk.Builder()
        self.builder.add_from_file('ui.glade')
        self.url = self.builder.get_object('url')
        self.api_url = self.builder.get_object('api_url')
        self.client_id = self.builder.get_object('client_id')
        self.client_secret = self.builder.get_object('client_secret')
        self.grant_type = self.builder.get_object('grant_type')
        self.txt_result = self.builder.get_object('txt_result')
        # a text buffer (stores text)
        self.text_buffer = self.txt_result.get_buffer()

        # ----- Connect element with signal
        self.window = self.builder.get_object('window')
        self.window.connect('destroy', self.destroy)
        self.config = context.get('config', False)

        # ----- Events
        self.url.set_text(self.config['auth0']['url'])
        self.api_url.set_text(self.config['auth0']['api_url'])
        self.client_id.set_text(self.config['auth0']['client_id'])
        self.client_secret.set_text(self.config['auth0']['client_secret'])
        self.grant_type.set_text(self.config['auth0']['grant_type'])
        self.button_autentica = self.builder.get_object('button_autentica')
        self.button_autentica.connect(
            'clicked', self.on_button_autentica_clicked)

    def destroy(self, widget=None, data=None):
        if self.parent and self.parent.window:
            self.parent.window.show()
        self.window.destroy()
        if self.is_main:
            Gtk.main_quit()

    def show(self):
        # ----- If class come from a parent, hide it
        if self.parent and self.parent.window and not self.is_modal:
            self.parent.window.hide()
        if self._maximize:
            self.window.maximize()
        self.window.show()
        # ----- If class is a main class, launch gtk main
        if self.is_main:
            Gtk.main()

    def on_button_force_exit_clicked(self, widget, data=None):
        Gtk.main_quit()

    def on_button_autentica_clicked(self, widget, data=None):
        conn = http.client.HTTPSConnection(self.url.get_text())

        payload = "{"
        payload = payload + "\"client_id\":\"{}\",".format(self.client_id.get_text())
        payload = payload + "\"client_secret\":\"{}\",".format(self.client_secret.get_text())
        payload = payload + "\"audience\":\"{}\",".format(self.api_url.get_text())
        payload = payload + "\"grant_type\":\"{}\"".format(self.grant_type.get_text())
        payload = payload + "}"

        headers = {'content-type': "application/json"}

        conn.request("POST", "/oauth/token", payload, headers)

        res = conn.getresponse()
        data = res.read()

        self.text_buffer.set_text(str(data.decode("utf-8")))


def run_software():
    config = configparser.ConfigParser()
    config.read('config.ini')

    UI(context={
        'config': config,
        }).show()


if __name__ == '__main__':
    run_software()

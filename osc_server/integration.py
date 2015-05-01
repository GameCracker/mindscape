#!/usr/bin/env python
import urllib2
import requests
import time
import datetime
import json
import numpy as np
import mne
import sys
import os
import socket
# import Tkinter as tk
# print os.path.dirname(os.path.realpath(__file__))
from pySpacebrew.spacebrew import Spacebrew


# print time.time()
# st = datetime.datetime.fromtimestamp(1418446050).strftime('%Y-%m-%d %H:%M:%S')
# st1 = datetime.datetime.fromtimestamp(1418446051).strftime('%Y-%m-%d %H:%M:%S')
# print st
# print st1

SERVER_IP = "server.neuron.brain"
UDP_IP = "127.0.0.1"
UDP_PORT = 8052

class Integration(object):

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.count = 0
        self.calc_range = 1
        self.raw = []
        self.alpha_min = self.beta_min = sys.float_info.max
        self.alpha_max = self.beta_max = sys.float_info.min
        self.timestamp = str(datetime.datetime.now().isoformat())

    def get_data(self):
        count = 0
        last_time = time.time()
        while True:
            cur = time.time()
            if cur != last_time or count == 0:
                end = int(cur)
                start = int(cur) - 1
                st = datetime.datetime.fromtimestamp(int(time.time()))
                req = "http://cloudbrain.rocks/data?userId=1&metric=eeg&start=%d&end=%d" % (start, end)
                r = requests.get(req)
                print r.status_code
                print r.headers
                print type(r.content)
                print r.content
                last_time = cur
            count += 1

    def spacebrew_data(self):
        r = requests.get("http://cloudbrain.rocks/link?metric=eeg&publisher=muse-001&subscriber=cloudbrain")
        print r.status_code
        print r.headers
        print type(r.content)
        print r.content

    def spacebrew_pub_test(self):
        data = "hi unity!!!!!!!!!!!!!!"
        name = "booth-6-pub"
        server = "localhost"
        sb = Spacebrew(name, server=server)
        sb.addPublisher("test-pub", "string")
        sb.addSubscriber("test-sub", "string")
        sb.subscribe("test-sub", self.sb_handler)
        sb.start()
        print "**************streaming starts**************"
        # time.sleep(10)
        # while True:
        #     sb.publish("test-pub", data)

    def spacebrew_connect(self):
        name = "booth-6"
        # server = "server.neuron.brain"
        local_server = "localhost"
        sb = Spacebrew(name, server=SERVER_IP)
        sb.addPublisher("test pub", "string")
        sb.addSubscriber("eeg", "string")
        sb.addSubscriber("connect", "string")
        sb.addSubscriber("disconnect", "string")
        sb.addSubscriber("mellow", "string")
        sb.addSubscriber("alpha_relative", "string")
        sb.addSubscriber("beta_relative", "string")
        sb.addSubscriber("gamma_relative", "string")
        # sb.subscribe("eeg", self.eeg_handler_test)
        sb.subscribe("eeg", self.sb_eeg_handler)
        sb.subscribe("connect", self.sb_connect_handler)
        sb.subscribe("disconnect", self.sb_disconnected_handler)
        sb.subscribe("mellow", self.sb_mellon_handler)
        sb.subscribe("alpha_relative", self.sb_alpha_handler)
        sb.subscribe("beta_relative", self.sb_alpha_handler)
        sb.subscribe("gamma_relative", self.sb_gamma_handler)
        # data from local muse
        data = "test"
        sb.start()
        print "---------------streaming starts---------------"
        # time.sleep(60)
        # while True:
        #     sb.publish("test pub", data)

    def sb_gamma_handler(self, value):
        msg = "gamma:" + value
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    def sb_beta_handler(self, value):
        msg = "beta:" + value
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    def sb_alpha_handler(self, value):
        msg = "alpha:" + value
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    def sb_mellon_handler(self, value):
        msg = "mellon:" + value
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    def sb_handler(self, value):
        print "++++++++++++++++++++++++++"
        print value

    def sb_connect_handler(self, value):
        print "connect: %s" % value
        msg = "connect:" + value
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    def sb_disconnected_handler(self, value):
        print "disconnected: %s" % value
        msg = "disconnect:" + value
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    def eeg_handler_test(self, value):
        print "eeg: %s" % value
        vals = value.split(',')
        self.raw.append(vals)
        if np.shape(self.raw)[0] == 110:
            if self.count >= 60 and self.calc_range == 1:
                self.calc_range = 0
            sec_raw = np.array(self.raw)
            v_sec = sec_raw.transpose()
            print np.shape(v_sec)
            self.raw = []
            # print "---------110--------"

    def sb_eeg_handler(self, value):
        # print value
        vals_str = value.split(',')
        vals = [float(e) for e in vals_str]
        self.raw.append(vals)
        if np.shape(self.raw)[0] == 110:
            if self.count >= 60 and self.calc_range == 1:
                self.calc_range = 0
            sec_raw = np.array(self.raw)
            v_sec = sec_raw.transpose()
            for i in xrange(4):
                cv = v_sec[i]
                print "line 135"
                alpha = mne.filter.band_pass_filter(x=cv, Fs=110, Fp1=7.5, Fp2=14.0)
                # avg_cv = np.average(cv)
                alpha = np.absolute(alpha)
                # print "line 138"
                # print alpha
                # print np.size(alpha)
                avg_alpha = np.average(alpha)
                # print "line 139"
                # print "avg_alpha: %.8f" % avg_alpha
                if self.calc_range == 1:
                    if avg_alpha < self.alpha_min:
                        self.alpha_min = avg_alpha
                    if avg_alpha > self.alpha_max:
                        self.alpha_max = avg_alpha
                else:
                    pass
                    alpha_norm = abs((avg_alpha - self.alpha_min)/(self.alpha_max - self.alpha_min))
                    print "alpha_norm: %.8f, alpha_max: %.8f, alpha_min: %.8f" % (alpha_norm, self.alpha_max, self.alpha_min)
                    self.sock.sendto("alpha_norm:" + str(alpha_norm), (UDP_IP, UDP_PORT))
                self.count += 1
            self.raw = []

    def get_data_test(self, ):
        start = "1418446050"
        end = "1418446950"
        req = "http://cloudbrain.rocks/data?userId=1&metric=eeg&start=%s&end=%s" % (start, end)
        r = requests.get(req)
        num = len(r.content)
        j = json.loads(r.content)
        c_sec = []
        for i in j:
            raw = i['value'][1:]
            c_sec.append(raw)
        ver_sec = (np.array(c_sec)).transpose()
        for i in xrange(4):
            cv = ver_sec[i]
            alpha = mne.filter.band_pass_filter(x=cv, Fs=num, Fp1=7.5, Fp2=14)
            avg_alpha = np.average(alpha)

if __name__ == '__main__':
    integrate = Integration()
    # integrate.spacebrew_pub_test()
    integrate.spacebrew_connect()


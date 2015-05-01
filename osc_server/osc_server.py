from liblo import *
import sys, time, csv, datetime, time, socket
import numpy as np
import mne


UDP_IP = "127.0.0.1"
UDP_PORT = 8052
MESSAGE = "Hello Unity server! --Client"


class MuseServer(ServerThread):
    # listen for message on port 5001
    def __init__(self):
        self.alpha_min = self.beta_min = sys.float_info.max
        self.alpha_max = self.beta_max = sys.float_info.min
        self.pre_alpha_min = 0.25
        self.pre_alpha_max = 3.25
        self.calc_range = 1
        self.raw = []
        self.count = 0
        self.timestamp = str(datetime.datetime.now().isoformat())
        self.if_to_file = 0
        if self.if_to_file == 1:
            self.data_path = '/Users/ziqipeng/Dropbox/bci/x/data/muse/osc_raw_'
            self.file = open('/Users/ziqipeng/Dropbox/bci/x/data/muse/osc_raw_' + self.timestamp, 'w')
            self.file.write('TP9,FP1,FP2,TP10,timestamp,duration\n')
            self.file.close()
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        ServerThread.__init__(self, 5001)

    # receive accelerometer data
    # @make_method('/muse/acc', 'fffii')
    # def acc_callback(self, path, args)://???
    #     acc_x, acc_y, acc_z, timestamp, duration = args
    #
    # # print "%s %f %f %f %d %d" % (path, acc_x, acc_y, acc_z, timestamp, duration)
    
    @make_method('/muse/elements/experimental/mellow', 'f')
    def mellow_callback(self, path, args):
        mellow, = args
        # print "mellow: %s %f" % (path, mellow)
        msg = "mellow:" + str(mellow)
        print msg
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    @make_method('/muse/elements/touching_forehead', 'i')
    def touching_forehead_callback(self, path, args):
        touching_forehead, = args
        msg = "touching_forehead:" + str(touching_forehead)
        print msg
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    # receive EEG data
    @make_method('/muse/eeg', 'ffffii')
    def eeg_callback(self, path, args):
        self.if_to_file = 0
        l_ear, l_forehead, r_forehead, r_ear, timestamp, duration = args
        # print "%s %f %f %f %f %d %d" % (path, l_ear, l_forehead, r_forehead, r_ear, timestamp, duration)
        value = [l_ear, l_forehead, r_forehead, r_ear, timestamp, duration]
        # print np.shape(value)
        # print type(value)
        vals = []
        for i in xrange(len(value)):
            vals.append(str(value[i]))
        # print value
        # print vals
        str_value = ','.join(vals)
        # print str_value
        if self.if_to_file == 1:
            self.file = open('/Users/ziqipeng/Dropbox/bci/x/data/muse/osc_raw_' + self.timestamp, 'a')
            self.file.write(str_value + '\n')
            self.file.close()
        # print "======================"
        # print file('/Users/ziqipeng/Dropbox/bci/x/data/muse/osc_' + self.timestamp).read()
        # print "++++++++++++++++++++++"
        self.raw.append(value)
        if np.shape(self.raw)[0] == 220:
            print "count %d" % self.count
            if self.count >= 60 and self.calc_range == 1:
                print "--------alpha_min: %.8f, alpha_max: %.8f--------" % (self.alpha_min, self.alpha_max)
                self.calc_range = 0
            # print "220!!!!!!!!!!!!!!!!"
            # print np.shape(self.raw)
            # print np.asarray(self.raw)
            sec_raw = np.array(self.raw)
            v_sec = sec_raw.transpose()
            for i in xrange(4):
                # print "line 54"
                cv = v_sec[i]
                alpha = mne.filter.band_pass_filter(x=cv, Fs=220, Fp1=7.5, Fp2=14)
                beta = mne.filter.band_pass_filter(x=cv, Fs=220, Fp1=14, Fp2=32)
                gamma = mne.filter.band_pass_filter(x=cv, Fs=220, Fp1=32, Fp2=64)
                # print "avg_alpha: %.8f" % avg_alpha
                # if avg_alpha > 1.7:
                # print "alpha high======="
                # elif avg_alpha < 1.4:
                # 	print "alpha low======="
                # else:
                # print "idk======="
                avg_cv = np.average(cv)
                avg_alpha = np.average(alpha)
                avg_beta = np.average(beta)
                avg_gamma = np.average(gamma)
                if self.calc_range == 1:
                    if avg_alpha < self.alpha_min:
                        self.alpha_min = avg_alpha
                    if avg_alpha > self.alpha_max:
                        self.alpha_max = avg_alpha
                else:
                    alpha_norm = abs((avg_alpha - self.alpha_min) / (self.alpha_max - self.alpha_min))
                    print "alpha_norm: %.8f" % alpha_norm
                    self.sock.sendto("alpha_norm:" + str(alpha_norm), (UDP_IP, UDP_PORT))
                # print "alpha_norm: %.8f, avg_alpha: %.8f, avg_beta: %.8f, avg_gamma: %.8f" % (alpha_norm, avg_alpha, avg_beta, avg_gamma)
                # print "avg_beta: %.8f" % avg_beta
                # print "avg_gamma: %.8f" % avg_gamma
                # if avg_alpha > avg_beta:
                # 	print "more meditated========================"
                # else:
                # 	print "more focus========================"
                # print "alpha: ", alpha
                # print "beta: ", beta
                self.count += 1
            self.raw = []

    @make_method('/muse/elements/experimental/mellow', 'f')
    def mellow_callback(self, path, args):
        mellow, = args
        print "mellow: %s %f" % (path, mellow)
        msg = "mellow:" + str(mellow)
        print msg
        self.sock.sendto(msg, (UDP_IP, UDP_PORT))

class MuseServer1(ServerThread):
    def __init__(self):
        self.alphas = []
        self.counth = 0
        self.countl = 0
        self.timestamp = str(datetime.datetime.now().isoformat())
        self.data_path = '/Users/ziqipeng/Dropbox/bci/x/data/muse/osc_focus_'
        self.file = open('/Users/ziqipeng/Dropbox/bci/x/data/muse/osc_focus_' + self.timestamp, 'w')

        self.file.write('TP9,FP1,FP2,TP10,timestamp,duration\n')
        self.file.close()
        ServerThread.__init__(self, 5001)
        self.tcp_ip = "127.0.0.1"
        self.tcp_port = 3000
        self.buffer_size = 4096
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.sock.connect((self.tcp_ip, self.tcp_port))
        self.msg = ""

    @make_method('/muse/elements/alpha_absolute', 'ffff')
    def eeg_callback(self, path, args):
        l_ear, l_forehead, r_forehead, r_ear = args
        alphas = [l_ear, l_forehead, r_forehead, r_ear]
        count = 0
        for i in alphas:
            if i > 0.4:
                print "one channel alpha higher than 0.4"
                count += 1
        if count >= 2:
            print "%d channels alpha high" % count
            self.counth += 1
        else:
            self.counth = 0
        if self.counth == 3:
            print "1"
            self.msg = 1
            self.counth = 0
        else:
            print "0"
            self.msg = 0
        # self.sock.send(str(self.msg))
        print "alpha_absolute: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/beta_absolute', 'ffff')
    # def eeg_callback(self, path, args):
    # l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "beta_absolute: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/delta_absolute', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "delta_absolute: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/gamma_absolute', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "gamma_absolute: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/theta_absolute', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "theta_absolute: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/alpha_relative', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "alpha_relative: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/beta_relative', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "beta_relative: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/delta_relative', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "delta_relative: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/gamma_relative', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "gamma_relative: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/theta_relative', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "theta_relative %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/horseshoes', 'ffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "horseshoes: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/blink', 'i')
    # def eeg_callback(self, path, args):
    # 	blink, = args
    # 	print "blink: %s %d" % (path, blink)

    # @make_method('/muse/elements/jaw_clench', 'i')
    # def eeg_callback(self, path, args):
    # 	jaw_clench, = args
    # 	print "jaw_clench: %s %d" % (path, jaw_clench)

    # @make_method('/muse/elements/is_good', 'iiii')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "is_good: %s %d %d %d %d" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # @make_method('/muse/elements/touching_forehead', 'i')
    # def eeg_callback(self, path, args):
    # 	touching_forehead, = args
    # 	print "touching_forehead: %s %d" % (path, touching_forehead)

    # @make_method('/muse/elements/experimental/concentration', 'f')
    # def eeg_callback(self, path, args):
    # 	concentration, = args
    # 	print "concentraction: %s %f" % (path, concentration)

    # @make_method('/muse/elements/experimental/mellow', 'f')
    # def eeg_callback(self, path, args):
    # 	mellow, = args
    # 	print "mellow: %s %f" % (path, mellow)
    #    msg = "mellon:" + str(mellow)
    #    print msg
    #    self.sock.sendto(msg, (UDP_IP, UDP_PORT))

    # @make_method('/muse/elements/raw_fft0', 'fffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff')
    # def eeg_callback(self, path, args):
    # 	l_ear, l_forehead, r_forehead, r_ear = args
    # 	print "raw_fft0: %s %f %f %f %f" % (path, l_ear, l_forehead, r_forehead, r_ear)

    # handle unexpected messages
    @make_method(None, None)
    def fallback(self, path, args, types, src):
        # print "Unknown message \
        # \n\t Source: '%s' \
        # \n\t Address: '%s' \
        # \n\t Types: '%s' \
        # \n\t Payload: '%s'" \
        # % (src.url, path, types, args)
        pass


try:
    server = MuseServer()
except ServerError, err:
    print str(err)
    sys.exit()

server.start()

if __name__ == "__main__":
    while 1:
        time.sleep(1)


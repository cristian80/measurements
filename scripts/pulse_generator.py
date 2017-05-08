
import numpy as np 
import pylab as plt

# we use the tinyrpc package to connect to the JSON-RPC server
from tinyrpc.protocols.jsonrpc import JSONRPCProtocol
from tinyrpc.transports.http import HttpPostClientTransport
from tinyrpc import RPCClient

# binary and base64 conversion
import struct
import base64





class PulseSequence ():

	def __init__(self):
		self.sequence = {'D0':[], 'D1':[], 'D2':[], 'D3':[], 'D4':[], 'D5':[], 'D6':[], 'D7':[]}
		self.generator_sequence = []
		self.seq_timers = [0,0,0,0,0,0,0,0]
		self.active_ch = None
		self.sequence_duration = 0

	def add_dig_pulse (self, duration, channel):
		if ((channel>0)&(channel<=7)):
			self.sequence['D'+str(channel)].append ([1, duration])
			self.seq_timers[channel] += duration
		else:
			print ('Specified channel does not exist!')

	def add_wait_pulse (self, duration, channel):
 		if ((channel>0)&(channel<=7)):
			self.sequence['D'+str(channel)].append ([0, duration])
			self.seq_timers[channel] += duration
		else:
			print ('Specified channel does not exist!')

	def select_active_channels (self):
		max_t = max(self.seq_timers)
		self.active_ch = np.nonzero(self.seq_timers)[0]

		seq_active_ch = {}
		for i in self.active_ch:
			seq_active_ch ['D'+str(i)] = self.sequence ['D'+str(i)]
			if self.seq_timers[i]<max_t:
				self.add_wait_pulse (duration=max_t-self.seq_timers[i], channel = i)
		
		self.sequence = seq_active_ch
		l = self.seq_timers
		self.seq_timers = np.zeros(len(self.active_ch))
		j = 0
		for i in self.active_ch:
			self.seq_timers[j] = int(l[i])
			j += 1

		self.nr_active_chans = len (self.active_ch)
		self.sequence_duration = max_t


	def pop_out (self):

		durations = np.zeros(self.nr_active_chans)
		values = np.zeros(self.nr_active_chans)

		for i in np.arange(self.nr_active_chans):
			ch = self.active_ch[i]
			durations[i] = self.sequence['D'+str(ch)][0][1]
			values[i] = self.sequence['D'+str(ch)][0][0]

		min_dur = min(durations)
		min_ch = self.active_ch[np.argmin(durations)]

		print 'Minimum duration: ', min_dur, ' at channel: ', min_ch

		v = 0
		for i in np.arange(self.nr_active_chans):
			ch = self.active_ch[i]
			d = durations[i]
			v = v+(2**ch)*values[i]
			if ((d-min_dur)>0):
				self.sequence ['D'+str(ch)][0][1] = self.sequence ['D'+str(ch)][0][1] - min_dur
			else:
				self.sequence ['D'+str(ch)] = self.sequence ['D'+str(ch)][1:]

		self.sequence_duration = self.sequence_duration - min_dur
		return min_dur, str(hex(v))[:-1]

	def generate_pulse_streamer_sequence (self):

		self.pulse_streamer_seq = []
		while (self.sequence_duration>0):
			t, value = self.pop_out()
			self.pulse_streamer_seq.append([t, value, hex(0), hex(0)])

		print self.pulse_streamer_seq

	def print_seq (self):
		print 'Pulse Sequence:'
		print self.sequence


class PulseStreamer():

	def __init__(self, ip = '192.168.1.100'):
		self.ip = ip
		self.url = 'http://'+self.ip+':8050/json-rpc'
		self.client = RPCClient(
	    	JSONRPCProtocol(),
	    	HttpPostClientTransport(self.url)
			)

		self.ps = self.client.get_proxy()

	def load_sequence (self, sequence):
		self.sequence = sequence
	
	def get_random_seq(min_len=0, max_len=1024, n_pulses=1000):
	    """
	    Generate a sequence of random pulses on the digital
	    channels 1-7 and the two analog channels.
	    
	    Digital channel 0 is used as a trigger.    
	    """
	    t = np.random.uniform(min_len, max_len, n_pulses).astype(int)
	    seq = [ (8, 1, 0, 0) ] # 8 ns trigger pulse on channel 0
	    for i, ti in enumerate(t):
	        state = i%2
	        seq += [ (ti, 0xfe*state, 0x7fff*state, -0x7fff*state) ]
	    return seq

	def encode(seq):
	    """
	    Convert a human readable python sequence to a base64 encoded string
	    """
	    s = b''
	    for pulse in seq:
	        s+=struct.pack('>IBhh', *pulse)
	    return base64.b64encode(s)


	def pulse_sequence ():
	    """
	    trigger on channel 0
	    signal on channel 1
	    """

	    t_ns = 200
	    seq = [(8,1,0,0)]
	    for i in np.arange(100):
	        state = i%2
	        seq += [(t_ns, 2*state, 0, 0)]
	    return seq

	def set_parameters (self, n_runs = -1, initial = (0,0xff,0,0), 
			final = (0,0x00,0x7fff,0), underflow = (0,0,0,0), start = 'IMMEDIATE'):

		self.n_runs = n_runs
		self.initial = initial
		self.final = final
		self.underflow = underflow
		self.start = start

	def stream (self):
		self.ps.stream(self.encode(self.sequence), self.n_runs, 
					self.initial, self.final, self.underflow, self.start)


	'''



	#seq = get_random_seq(n_pulses=1000)
	seq = pulse_sequence()



	print (seq)
	#plt.plot (sec)
	print('Pulse Streamer is running: '+str(ps.isRunning()))

	'''


p = PulseSequence()
p.add_dig_pulse (duration = 50, channel = 3)
p.add_wait_pulse (duration = 150, channel = 3)
p.add_dig_pulse (duration = 100, channel = 3)
p.print_seq()

p.add_dig_pulse (duration = 100, channel = 5)
p.add_wait_pulse (duration = 50, channel = 5)
p.add_dig_pulse (duration = 200, channel = 5)
p.print_seq()

p.add_dig_pulse (duration = 25, channel = 1)
p.print_seq()


p.select_active_channels()
p.print_seq()

p.generate_pulse_streamer_sequence()
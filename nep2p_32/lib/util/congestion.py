import random
import time, math
from common import printf
from config import *

'''
	Expected to be run these in senders
'''
class Congestion:
	#delay-related parameters
	#DELAY_P_RATIO = 0.01
	#DELAY_I_RATIO = -0.5
	#DELAY_D_RATIO = 0.005
	#I_BOUND = 100
	#I_FACTOR = 16.0
	#P_BASE = 16.0
	DELAY_TARGET = conf['congestion_target'] if 'congestion_target' in conf else 0.1 #the target expected delay_pid value
	#PKT_TARGET = 0.8

	#send rate related parameters
	GAIN = conf['congestion_gain'] if 'congestion_gain' in conf else 5 #normal gain without congestion
	#MIN_SEND_RATE = 1 #minimum window
	#MAX_SEND_RATE = 999999999 #bound the speed
	INIT_SEND_RATE = 100 #same as MIN_CWND?
	ALLOWED_INCREASE = conf['congestion_allowedincrease'] if 'congestion_allowedincrease' in conf else 100 #upper bound of the send_rate gain
	ALLOWED_DECREASE = conf['congestion_alloweddecrease'] if 'congestion_alloweddecrease' in conf else -100
	THRESHOLD = conf['congestion_threshold'] if 'congestion_threshold' in conf else 0.2 #update threshold
	BASE_DELAYS_ROLLOVER = conf['congestion_rollover'] if 'congestion_rollover' in conf else 1 #seconds
	BASE_DELAYS_LEN = conf['congestion_len'] if 'congestion_len' in conf else 10 #array length

	#ADD_STEP = 80 #10
	#DROP_STEP = 40
	#UPDATE_DELAY = 30 #15
	#DELAY_FACTOR = 500
	MIN_RATE = conf['congestion_minrate'] if 'congestion_minrate' in conf else 1
	MAX_RATE = 999999999
	#SPEED_THRESHOLD = 10
	DEBUG = conf['congestion_debug'] if 'congestion_debug' in conf else False
	PRINT_ACK = conf['congestion_printack'] if 'congestion_printack' in conf else True
	FILTER = conf['congestion_filter'] if 'congestion_filter' in conf else False
	ADJUST = conf['congestion_adjust'] if 'congestion_adjust' in conf else False
	FILTER_ZEROS = conf['congestion_zeros'] if 'congestion_zeros' in conf else True
	ENABLE_SEND_RECV = conf['congestion_sendrecv'] if 'congestion_sendrecv' in conf else False
	ENABLE_SEND_RECV2 = conf['congestion_sendrecv2'] if 'congestion_sendrecv2' in conf else True
	PRATIO = conf['congestion_pratio'] if 'congestion_pratio' in conf else True
	SKIP_NUM = conf['congestion_skipnum'] if 'congestion_skipnum' in conf else 4
	RATIO_GAIN = conf['congestion_ratiogain'] if 'congestion_ratiogain' in conf else 1
	BOUND_OFFTARGET = conf['congestion_offtarget'] if 'congestion_offtarget' in conf else True
	IGNORE_DELAY = conf['congestion_ignoredelay'] if 'congestion_ignoredelay' in conf else False
	FIXED_SPEED = conf['congestion_fixedspeed'] if 'congestion_fixedspeed' in conf else 0

	def __init__(self):
		#will be reset in connection
		self.send_rate = Congestion.INIT_SEND_RATE

		self.last_delay = Congestion.DELAY_TARGET
		self.num_received = 0
		self.num_ack = 0
		self.num_sent = 1
		self.last_num_received = 0
		self.last_num_sent = 1
		self.last_ratio = 1.0

		self.last_rollover = 0
		self.base_delays = []

	def filter_delay(self, values):
		#return sum(values)/len(values)
		l = len(values)
		cut = int(0.05*l)
		start,end = cut, l-cut
		newv = sorted(values)[start:end]
		#printf("len=%d cut_len=%d\n\tori(max,min)=%.4f,%.4f\n\tnew(max,min)=%.4f,%.4f"%(l,end-start,max(values),min(values),max(newv),min(newv)), "filter", RED)
		#print '[[values]]',
		#for i in values:
		#	print '%.2f'%(i*100),
		#print ''
		return newv

		if len(values) <= 4:
			#return sum(values)/len(values)
			return values
		n = 0
		Sum = 0
		Sum_sqr = 0
		for x in values:
			n += 1
			Sum += x
			Sum_sqr += x*x
		variance = (Sum_sqr - ((Sum*Sum)/n))/(n - 1)
		v = sorted(values)
		median = v[n/2]
		printf("variance=%.4f median=%.4f mean=%.4f"%(variance, median, sum(v)/len(v)), "filter", RED)
		v = [i for i in values if abs(i-median)<variance*2]
		#return sum(v)/len(v)
		return v

	def update_base_delays(self, delays):
		t = time.time()
		if t-self.last_rollover > Congestion.BASE_DELAYS_ROLLOVER:
			if len(self.base_delays)>Congestion.BASE_DELAYS_LEN:
				self.base_delays.reverse()
				self.base_delays.pop()
				self.base_delays.reverse()
			self.base_delays.append(delays[0])
			self.last_rollover = t
		elif len(self.base_delays)>0:
			self.base_delays.append(
				min(self.base_delays.pop(), min(delays))
			)
		else:
			self.base_delays.append(min(delays))

	'''
		ack_pkt: list of one-way time differences
	'''
	def on_acknowledgement(self, ack_pkts):
		#self.send_rate = 10
		#self.change_max_bandwidth()
		#return
		l = len(ack_pkts)
		self.num_ack += l #len(ack_pkts)
		if l <= Congestion.SKIP_NUM:
			return
		#if random.randint(1,10) == 1:
			#printf("delay(l,c)=(%f,%f)\n\trate(r,t)=%d,%d"%(self.last_delay,delay,self.max_bandwidth,self.send_rate), "ACK", YELLOW)
			#r = 1.0*(self.num_received-self.last_num_received)/(self.num_sent-self.last_num_sent)
			#printf("last_delay=%f delay=%f\n\trate=%f max_up=%f\n\tlast=%d sent=%d recv=%d\n\tratio=%.3f"%(self.last_delay,delay,
			#		self.send_rate,self.max_bandwidth,self.last_num_sent, self.num_sent,self.num_received, r), "ACK", YELLOW)

		ack_pkts = [float(n) for n in ack_pkts]
		self.update_base_delays(ack_pkts)
		if Congestion.PRINT_ACK:
			print 'ack_pkts', ack_pkts
		if Congestion.FILTER_ZEROS:
			non_zeros = [i for i in ack_pkts if i>=1]
			if len(non_zeros) > l/2:
				ack_pkts  = non_zeros
		if Congestion.ADJUST and len(ack_pkts)>1:
			min_ack = min(ack_pkts)
			r = [i-min_ack for i in ack_pkts if i-min_ack!=0]
			if Congestion.PRINT_ACK:
				print 'r', r
			ack_pkts = r
			self.update_base_delays(ack_pkts)
		if Congestion.FILTER:
			filtered = self.filter_delay(ack_pkts)
		else:
			filtered = ack_pkts
		#delay = (self.last_delay+sum(filtered))/(len(filtered)+1)
		delay = self.last_delay
		for d in filtered:
			delay = (delay+d)/2
		self.last_delay = delay
		if Congestion.PRATIO:
			self.last_ratio = (self.last_ratio+1.0*self.num_ack/self.num_sent)/2
		else:
			self.last_ratio = 1.0*self.num_ack/self.num_sent
		diff = delay - min(self.base_delays)
		#:TODO: bound the off_target to 1 to bound the gain
		if Congestion.IGNORE_DELAY:
			off_target = 1
		elif Congestion.BOUND_OFFTARGET:
			off_target = min((Congestion.DELAY_TARGET-diff),Congestion.DELAY_TARGET)/Congestion.DELAY_TARGET
		else:
			off_target = (Congestion.DELAY_TARGET-diff)/Congestion.DELAY_TARGET
		step_gain = Congestion.GAIN*(10**(math.ceil(math.log10(int(self.send_rate)))))/self.send_rate
		if Congestion.ENABLE_SEND_RECV2:
			gain = step_gain * off_target * self.last_ratio * self.last_ratio
		if Congestion.ENABLE_SEND_RECV:
			gain = step_gain * off_target * self.last_ratio
		else:
			gain = step_gain * off_target * l / self.send_rate
		gain = min(Congestion.ALLOWED_INCREASE, max(Congestion.ALLOWED_DECREASE, gain))
		self.send_rate += gain * Congestion.RATIO_GAIN
		self.send_rate = max(Congestion.MIN_RATE, min(Congestion.MAX_RATE, self.send_rate))
		if Congestion.FIXED_SPEED:
			self.send_rate = Congestion.FIXED_SPEED
		if Congestion.DEBUG: # and random.randint(1,100) == 1:
			print "ack_pkts %.5f %.5f"%(min(ack_pkts), max(ack_pkts)),
			print "filtered %.5f %.5f"%(min(filtered), max(filtered))
			printf("len=%d pkts(s,r,a)=%d,%d,%d time=%.2f\n\tdelay(b,c,d)=(%f,%f,%f)\n\toff_target=%f rate(r,t)=%.2f,%.2f"%(l,self.num_sent,self.num_received,self.num_ack,time.time(),self.base_delays[-1],delay,diff,off_target,self.max_bandwidth,self.send_rate), "ACK", YELLOW)
		if abs(self.send_rate-self.max_bandwidth) > self.max_bandwidth*Congestion.THRESHOLD:
			self.change_max_bandwidth()

		'''
		if self.num_sent-self.last_num_sent > (self.max_bandwidth*4):
			dr = 1.0*(self.num_ack-self.last_num_ack)/(self.num_sent-self.last_num_sent)
			tr = 1.0*(self.num_ack)/(self.num_sent)
			r = (self.last_ratio+tr+dr*2)/4
			rand = random.randint(1,2)
			if rand == 1:
				printf("dr=%.3f tr=%.3f lr=%.3f r=%.3f\n\tlsent=%d sent=%d lrecv=%d recv=%d"%(
						dr,tr,self.last_ratio,r,
						self.last_num_sent, self.num_sent, self.last_num_ack, self.num_ack), "UPDATE", YELLOW)
			add_step = max(self.send_rate/8, Congestion.ADD_STEP)
			self.send_rate = self.send_rate+add_step if r > 0.9 else self.send_rate*3/4
			self.send_rate = min(Congestion.MAX_RATE, max(Congestion.MIN_RATE, self.send_rate))
			self.last_num_sent = self.num_sent
			self.last_num_ack = self.num_ack
			self.last_ratio = r
			if rand == 1:
				printf("rate=%f max_up=%f"%(
						self.send_rate,self.max_bandwidth), "UPDATE", YELLOW)
			self.change_max_bandwidth()
		'''
		#self.last_delay = (self.last_delay*(Congestion.DELAY_FACTOR-1)+delay)/Congestion.DELAY_FACTOR

	#:TODO: needed?
	def on_timeout(self):
		pass

	def change_max_bandwidth(self):
		return True
		#if abs(self.send_rate-self.max_bandwidth) > self.max_bandwidth*Congestion.THRESHOLD:
		#	return True
		#return False

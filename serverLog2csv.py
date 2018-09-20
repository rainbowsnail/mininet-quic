#!/bin/python
import os,sys,re
from optparse import OptionParser

sep = ','
sendList = {}
def parse(options):
	global sep
	global sendList
	srcFile = open(options.srcfile, 'r') 
	dstFile = open(options.dstfile, 'w')
	lines = srcFile.readlines()
	dstFile.write('Day' + sep + 'Time' + sep + 'PacketNum' + sep + 'Length' + sep + 'oood' + sep + 'rtt' '\n')
	i = 0
	lastPN = 0
	while i < len(lines):
		oood = False
		line = lines[i]
		if 'Server: Sending packet' in line:
			#[0918/161915.946294:VERBOSE1:quic_connection.cc(1522)] Server: Sending packet 7885 : data bearing , encryption level: ENCRYPTION_FORWARD_SECURE, encrypted length:1350
			#print line
			numList = re.findall('\d+\.?\d*', line)
			day = line[1:5]
			time = line[line.find('/')+1 : line.find(':')]
			packetNum = numList[-2]
			if packetNum < lastPN:
				oood = True
			length = numList[-1]
			dstFile.write(str(day) + sep + str(time) + sep + packetNum + sep +
						  length + sep + str(oood) + '\n')
			sendList[packetNum] = time
		elif 'Server: OnAckFrame' in line:
			#[0918/161907.446927:VERBOSE1:quic_connection.cc(708)] Server: OnAckFrame: { largest_observed: 2, ack_delay_time: 5880, packets: [ 1 2  ], received_packets: [ 1 at 6502489603650 2 at 6502489603961  ] }
			#print line
			day = line[1:5]
			time = line[line.find('/')+1 : line.find(':')]
			line = line[line.find(']')+1 : ]
			numList = re.findall("\d+\.?\d*",line)
			packetNum = numList[0]
			#ack_delay_time = numList[1]
			ack_delay_time = 0 
			if packetNum not in sendList:
				print "ack an unsent packet"
				continue
			#print numList
			#print packetNum
			#print ack_delay_time
			rtt = float(time) - float(sendList[packetNum]) - float(ack_delay_time)/1000000
			dstFile.write(str(day) + sep + str(time) + sep + packetNum + sep +
						  length + sep + str(oood) + sep + str(rtt) + '\n')
		i += 1

	srcFile.close()
	dstFile.close()

def main():
	parser = OptionParser(usage="usage: %prog [options] filename",
	                      version="%prog 1.0")
	parser.add_option("-s", "--src", action="store", dest="srcfile",
					  default="./server.log", help="server log file to be parsed")                    
	parser.add_option("-d", "--dst", action="store", dest="dstfile",
					  default="./server.csv", help="server result csv file name")
	(options, args) = parser.parse_args()

	parse(options)

if __name__ == '__main__':
    main()

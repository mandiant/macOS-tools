##########################################
##Author: James T. Bennett
##NIB file parser
##########################################

########################################################################
# Copyright 2017 FireEye
#
# FireEye licenses this file to you under the Apache License, Version
# 2.0 (the "License"); you may not use this file except in compliance with the
# License. You may obtain a copy of the License at:
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied. See the License for the specific language governing
# permissions and limitations under the License.
########################################################################

import ccl_bplist
import argparse

def getClassName(o):
	if 'NSClassName' in o:
		cn = o['NSClassName']
		if '$class' in cn:
			return cn['NS.string']
	else:
		cn = o['$class']['$classes'][0]
		if '$class' in cn:
			return cn['NS.string']

	return cn

def getContents(o):
	if 'NSCell' in o and 'NSContents' in o['NSCell']:
		if 'NS.string' in o['NSCell']['NSContents']:
			return o['NSCell']['NSContents']['NS.string']
		elif 'NSClassName' in o['NSCell']['NSContents']:
			return o['NSCell']['NSContents']['NSClassName']
		else:
			return o['NSCell']['NSContents']
	if 'NSTitle' in o:
			if 'NS.string' in o['NSTitle']:
				return o['NSTitle']['NS.string']
			else:
				return o['NSTitle']
	else:
		return None

def main():
	parser=argparse.ArgumentParser(description="NeXTSTEP Interface Builder (NIB) file parser prints a list of all connections defined in a NIB file")
	parser.add_argument('nibfile', help='path to a NIB file')

	args = parser.parse_args()
	with open(args.nibfile, "rb") as rp:
		plist = ccl_bplist.load(rp)

	nib = ccl_bplist.deserialise_NsKeyedArchiver(plist)

	ibcons = nib['IB.objectdata']['NSConnections']['NS.objects']
	for i in range(len(ibcons)):
		if 'NSLabel' not in ibcons[i]:
			continue

		lbl = ibcons[i]['NSLabel']
		id = dict(nib['IB.objectdata']['NSConnections'])['NS.objects'][i].value
		sname = "NA"
		srcid = "NA"
		dname = "NA"
		dstid = "NA"

		if 'NSSource' in ibcons[i]:
			srcid = dict(ibcons[i])['NSSource'].value
			src = ibcons[i]['NSSource']
			sname = getClassName(src)
			scontents = getContents(src)

		if 'NSDestination' in ibcons[i]:	
			dstid = dict(ibcons[i])['NSDestination'].value
			dst = ibcons[i]['NSDestination']
			dname = getClassName(dst)
			dcontents = getContents(dst)

		out = "%d: %s (%s) - %s " % (i, lbl, id, sname)
		if scontents:
			out += "[%s] " % scontents

		out += "(%s) ---> %s "  % (srcid, dname) 
		if dcontents:
			out += "[%s] " % dcontents
		
		out += "(%s)" % dstid
		print(out.encode("utf-8"))

if __name__ == '__main__':
    main()
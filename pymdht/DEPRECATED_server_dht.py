# Copyright (C) 2009-2010 Raul Jimenez
# Released under GNU LGPL 2.1
# See LICENSE.txt for more information

import ptime as time
import sys
import pdb
from optparse import OptionParser

#import guppy

import logging, logging_conf

logs_level = logging.DEBUG # This generates HUGE (and useful) logs
#logs_level = logging.INFO # This generates some (useful) logs
#logs_level = logging.WARNING # This generates warning and error logs
#logs_level = logging.CRITICAL

import identifier
import mdht#kadtracker


#hp = guppy.hpy()

def _on_peers_found(peers):
    if peers:
        print '[%.4f] %d peer(s)' % (time.time() - start_ts, len(peers))
    else:
        print '[%.4f] END OF LOOKUP' % (time.time() - start_ts)

def main(options, args):
    my_addr = (options.ip, options.port)
    logs_path = options.path
    logging_conf.setup(logs_path, logs_level)
    print 'Using the following plug-ins:'
    print '*', options.routing_m_file
    print '*', options.lookup_m_file
    routing_m_mod = __import__(options.routing_m_file[:-3])
    lookup_m_mod = __import__(options.lookup_m_file[:-3])
    dht = kadtracker.KadTracker(my_addr, logs_path,
                                routing_m_mod,
                                lookup_m_mod)
    try:
        info_hashes = open(options.infohash_file)
    except AttributeError:
        info_hashes = []
        print 'WARNING: no info_hashes file provided'

    try:
        print 'Warming up...',
        sys.stdout.flush()
        time.sleep(60)
        print 'DONE'
        print 'Type Control-C to exit.'
        for line in info_hashes:
            info_hash = identifier.Id(line.strip())
            print  '%s Getting peers for info_hash %r' % (
                time.asctime(), info_hash)
            dht.get_peers(info_hash, _on_peers_found)
            global start_ts
            start_ts = time.time()
            time.sleep(options.lookup_interval)

    except (KeyboardInterrupt):
        pass
    dht.stop()
    print '\nStopping DHT...',
    sys.stdout.flush()
    time.sleep(1)
    print 'DONE'
    
if __name__ == '__main__':
    parser = OptionParser()
    parser.add_option("-a", "--address", dest="ip",
                      metavar='IP', default='127.0.0.1',
                      help="IP address to be used")
    parser.add_option("-p", "--port", dest="port",
                      metavar='INT', default=7000,
                      help="port to be used")
    parser.add_option("-x", "--path", dest="path",
                      metavar='PATH', default='interactive_logs/',
                      help="state.dat and logs location")
    parser.add_option("-r", "--routing-plug-in", dest="routing_m_file",
                      metavar='FILE', default='routing_manager_p2.py',
                      help="file containing the routing_manager code")
    parser.add_option("-l", "--lookup-plug-in", dest="lookup_m_file",
                      metavar='FILE', default='lookup_manager_p2.py',
                      help="file containing the lookup_manager code")
    parser.add_option("-z", "--logs-level", dest="logs_level",
                      metavar='INT',
                      help="logging level")
    parser.add_option("-t", "--lookup-interval", dest="lookup_interval",
                      metavar='INT', default=60,
                      help="Lookup interval (in seconds)")
    parser.add_option("-i", "--infohash-file", dest="infohash_file",
                      metavar='FILE',
                      help="File containing info_hashes (one per line")
    

    (options, args) = parser.parse_args()
    
    main(options, args)



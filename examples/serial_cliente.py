import sys
import logging
from os.path import dirname, realpath, sep, pardir
library_path = dirname(realpath(__file__)) + sep + pardir
sys.path.append(library_path)

import getopt
import logging
import iec870ree
import iec870ree.serial
import iec870ree.protocol
import datetime

def run_example(port, der, dir_pm, clave_pm):
    end_date = datetime.datetime.now()
    start_date = end_date - datetime.timedelta(days = 2)
    
    physical_layer = iec870ree.serial.Serial(port)
    link_layer = iec870ree.protocol.LinkLayer(der, dir_pm)
    link_layer.initialize(physical_layer)
    app_layer = iec870ree.protocol.AppLayer()
    app_layer.initialize(link_layer)

    physical_layer.connect()
    link_layer.link_state_request()
    link_layer.remote_link_reposition()
    logging.info("before authentication")
    resp = app_layer.authenticate(clave_pm)
    logging.info("CLIENTE authenticate response {}".format(resp))
    logging.info("before read")
    for resp in app_layer.read_integrated_totals(start_date, end_date):
        logging.info("read response {}".format(resp))
    app_layer.finish_session()
    physical_layer.disconnect()
    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    argv = sys.argv[1:]
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"hp:n:d:p:c:",
                                   ["port=", "der=", "dir_pm=",
                                   "clave_pm="])
    except getopt.GetoptError:
       logging.error('wrong command')
       sys.exit(2)

    port = "/dev/ttyUSB0"
    der = None
    dir_pm = None
    clave_pm = None
    for opt, arg in opts:
        if opt == '-h':
          logging.error("help not implemented")
          sys.exit()
        elif opt in ("-p", "--port"):
          port = arg
        elif opt in ("-d", "--der"):
          der = int(arg)
        elif opt in ("-p", "--dir_pm"):
          dir_pm = int(arg)
        elif opt in ("-c", "--clave_pm"):
          clave_pm = int(arg)

    logging.info('Started {} {} {} {}'.format(port, der, dir_pm,
                                                 clave_pm))
    run_example(port, der, dir_pm, clave_pm)

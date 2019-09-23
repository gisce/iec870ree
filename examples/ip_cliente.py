import sys
import logging
from os.path import dirname, realpath, sep, pardir
library_path = dirname(realpath(__file__)) + sep + pardir
sys.path.append(library_path)

import getopt
import logging
import iec870ree.ip
import iec870ree.protocol
import datetime


def run_example(ip, port, der, dir_pm, clave_pm):
    try:
        physical_layer = iec870ree.ip.Ip((ip, port))
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
        resp = app_layer.get_info()
        logging.info("read response get_info{}".format(resp.content))

        # DAILY BILLINGS
        #register = 'daily_billings'
        #logging.info("Getting {} absolute curve".format(register))
        #for resp in app_layer.read_incremental_values(
        #    datetime.datetime(2019, 8, 1, 0, 0),
        #    datetime.datetime(2019, 9, 1, 0, 0),
        #    register=register
        #):
        #    logging.info("read response {}".format(resp.content))

        #GET METER DATETIME
        resp = app_layer.read_datetime()
        logging.info("read response read_datetime {}".format(resp.content))
        now = datetime.datetime.now()
        meter_date = resp.content.tiempo.datetime
        diff = (now - meter_date).total_seconds()
        logging.info("NOW {}".format(now))
        logging.info("METER DATETIME {}".format(meter_date))
        logging.info("DIFF {}".format(diff))

        # GET SAVETIME DATES CHANGE
        resp = app_layer.get_savetime_dates()
        logging.info("read response get_savetime_dates {}".format(resp.content))

        # SET DATETIME
        #resp = app_layer.set_datetime()
        #logging.info("read response set_datetime {}".format(resp.content))
        #resp = app_layer.get_contracted_powers()
        #logging.info("read response contracted powers {}".format(resp.content))
        #for resp in app_layer.get_info():
        #    logging.info("read response get_info {}".format(resp))
    except Exception as e:
        print(e)
        raise
    finally:
        app_layer.finish_session()
        physical_layer.disconnect()
        sys.exit(1)

    
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    argv = sys.argv[1:]
    try:
        argv = sys.argv[1:]
        opts, args = getopt.getopt(argv,"i:hp:d:r:c:",
                                   ["ip=", "port=",
                                    "der=", "dir_pm=", "clave_pm="])
    except getopt.GetoptError:
       logging.error('wrong command')
       sys.exit(2)

    ip = None
    port = None
    der = None
    dir_pm = None
    clave_pm = None
    for opt, arg in opts:
        if opt == '-h':
          logging.error("help not implemented")
          sys.exit()
        elif opt in ("-p", "--port"):
          port = int(arg)
        elif opt in ("-i", "--ip"):
          ip = arg
        elif opt in ("-d", "--der"):
          der = int(arg)
        elif opt in ("-r", "--dir_pm"):
          dir_pm = int(arg)
        elif opt in ("-c", "--clave_pm"):
          clave_pm = int(arg)

    logging.info('Started {} {} {} {} {}'.format(ip, port,
                                                 der, dir_pm, clave_pm))
    run_example(ip, port, der, dir_pm, clave_pm)

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
 
        ##### CURRENT MEASURE (133)
        #logging.info("LEER CIERRES ACTUALES")
        #for resp in app_layer.current_tariff_info(register=1):
        #    logging.info("read response current_tariff_info (Cierres actuales) {}".format(resp))

        ##### CIERRES (136)
        #logging.info("LEER CIERRES DE FEBRERO")
        #for resp in app_layer.stored_tariff_info(
        #        datetime.datetime(2021, 1, 1, 1, 0),
        #        datetime.datetime(2021, 2, 1, 0, 0)):
        #    logging.info("read response stored_tariff_info (Cierres) {}".format(resp))

        ##### Configuration
        #resp = app_layer.get_configuration()
        #logging.info("read response get_configuration {}".format(resp))

        ##### DAILY BILLINGS
        #logging.info("GETTING DAILY BILLINGS")
        # ABSOLUTE (122)
        #for resp in app_layer.read_absolute_values(datetime.datetime(2020,2,1,0,0,0), datetime.datetime.now(), register='daily_billings'):
        #    logging.info("Daily billings response {}".format(resp))
        # INCREMENTAL (123)
        #logging.info("LEER CURVA DESDE ABRIL")
        #for resp in app_layer.read_incremental_values(datetime.datetime(2021, 4, 1, 0, 0, 0), datetime.datetime.now(), register='daily_billings'):
        #    logging.info("Daily billings response {}".format(resp))

        ##### DAILY BILLINGS
        #logging.info("GETTING DAILY BILLINGS")
        # ABSOLUTE (122)
        #for resp in app_layer.read_absolute_values(datetime.datetime(2020,2,1,0,0,0), datetime.datetime.now(), register='daily_billings'):
        #    logging.info("Daily billings response {}".format(resp))
        # INCREMENTAL (123)
        #logging.info("LEER CURVA DESDE ABRIL")
        #for resp in app_layer.read_incremental_values(datetime.datetime(2021, 4, 18, 0, 0, 0), datetime.datetime.now(), register='profiles'):
        #    logging.info("Daily billings response {}".format(resp))

        #### SET TIME ####
        #resp = app_layer.read_datetime()
        #logging.info("read response read_datetime {}".format(resp.content))
        #now = datetime.datetime.now()
        #meter_date = resp.content.tiempo.datetime
        #diff = (now - meter_date).total_seconds()
        #logging.info("NOW {}".format(now))
        #logging.info("METER DATETIME {}".format(meter_date))
        #logging.info("DIFF {}".format(diff))
        #resp = app_layer.set_datetime()
        #logging.info("read response set_datetime {}".format(resp.content))

        #### CONTRACTED POWERS
        #resp = app_layer.get_contracted_powers()
        #logging.info("read response contracted powers {}".format(resp.content))
        #for resp in app_layer.get_info():
        #    logging.info("read response get_info {}".format(resp))


        #### INSTANT_VALUES_OBJECTS name or code (Extended)
        logging.info("LEER VALORES INSTANTANEOS {}")
        instant_objects = ['totalizadores', 'potencias', 'I_V']
        logging.info("Get instant values")
        resp = app_layer.ext_read_instant_values(objects=instant_objects)
        print(resp.content)

        #### PROGRAMED TARIFFS (Extended)
        logging.info("LEER TARIFA PROGRAMADA")
        #tariff_objects = ['special_days', 'seasons', 'latent_activation_date', 'current_period']
        tariff_objects = ['seasons']
        logging.info("Get programmed tariff")
        resp = app_layer.ext_read_contract_tariff_info(register=134, objects=tariff_objects)
        print(resp.content)

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

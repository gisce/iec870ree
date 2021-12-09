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
import click
try:
    from urllib.parse import urlparse
except:
    from urlparse import urlparse

def run_example(ip, port, der, dir_pm, clave_pm):
    try:
        physical_layer = iec870ree.ip.Ip((ip, port))
        link_layer = iec870ree.protocol.LinkLayer(der, dir_pm)
        link_layer.initialize(physical_layer)
        app_layer = iec870ree.protocol.AppLayer()
        app_layer.set_content_timeout(300)
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

        ##### CURVES
        #logging.info("GETTING DAILY BILLINGS")
        # ABSOLUTE (122)
        #for resp in app_layer.read_absolute_values(datetime.datetime(2020,2,1,0,0,0), datetime.datetime.now(), register='profiles'):
        #    logging.info("Daily billings response {}".format(resp))
        #INCREMENTAL (123)
        logging.info("LEER CURVA")
        for resp in app_layer.read_incremental_values(datetime.datetime(2021, 4, 18, 0, 0, 0), datetime.datetime.now(), register='profiles'):
            logging.info("Profile response {}".format(resp))

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
        # logging.info("LEER VALORES INSTANTANEOS {}")
        # instant_objects = ['totalizadores', 'potencias', 'I_V']
        # logging.info("Get instant values")
        # resp = app_layer.ext_read_instant_values(objects=instant_objects)
        # print(resp.content)
        #
        # #### PROGRAMED TARIFFS (Extended)
        # logging.info("LEER TARIFA PROGRAMADA")
        # #tariff_objects = ['special_days', 'seasons', 'latent_activation_date', 'current_period']
        # tariff_objects = ['seasons']
        # logging.info("Get programmed tariff")
        # resp = app_layer.ext_read_contract_tariff_info(register=134, objects=tariff_objects)
        # print(resp.content)

        logging.info("LEER DIAS FESTIVOS")
        resp = app_layer.read_holiday_days()
        print(resp.content)

    except Exception as e:
        print(e)
        raise
    finally:
        app_layer.finish_session()
        physical_layer.disconnect()
        sys.exit(1)


def get_connection(url):
    url = urlparse(url)
    # PATH is TM connection params in format DER,PM,PWD
    der, pm, pwd = url.path.replace('/', '').split(',')
    host =url.hostname
    port =url.port

    logging.info('Started {} {} {} {} {}'.format(host, port, der, pm, pwd))
    return {'host': url.hostname, 'port': url.port, 'der': der,'dir_pm': pm, 'pwd': pwd}

@click.command()
@click.option('-u', '--url',
              help='URL to connect to meter (server:port/DER,PM,PASS)',
              type=str, default='iec://127.0.0.1:2000/1,1,1', show_default=True)
def connect_meter(url):
    logging.basicConfig(level=logging.INFO)
    conn_data = get_connection(url)

    run_example(
        conn_data['host'],
        int(conn_data['port']),
        int(conn_data['der']),
        int(conn_data['dir_pm']),
        int(conn_data['pwd'])
    )

if __name__ == "__main__":
    connect_meter()

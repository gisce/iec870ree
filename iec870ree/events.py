# -*- coding: utf-8 -*-
#{ 'SPA1': {'SPQ1': {'description': 'blabla', 'SPI': False, 'register': 52},
#           'SPQ2': {'description': '{SPI} bleble', 'SPI': ('perdida', 'recuperación'), 'register': 52},
#            ...
#          },
#{ 'SPA2': {'SPQN': {'description': 'blabla', 'SPI': False, 'register': 52},
#           'SPQN+1': {'description': '{SPI} bleble', 'SPI': ('perdida', 'recuperación'), 'register': 53},
#          },
# ....
#}
TM_EVENTS_DICT = {
    1:
        {
            1: {
                'spi': False,
                'register': '52',
                'description': 'rearranque de sistema (con pérdida de los datos anteriores al arranque)'
            },
            2: {
                'spi': False,
                'register': '52',
                'description': 'arranque tras fallo de alimentación (se conservan datos, parámetros y\nhora). A usar con dirección de registro'
            },
        },
    3:  {
            0: {
                'spi': False,
                'register': '52',
                'description': 'rearranque de sistema (con pérdida de los datos anteriores al arranque)'
            },
            1: {
                'spi': ['Fin', 'Inicio'],
                'register': '52',
                'description': '{} fallo de tensión de medida en fase 1'
            },
            2: {
                'spi': ['Fin', 'Inicio'],
                'register': '52',
                'description': '{} fallo de tensión de medida en fase 2'
            },
            3: {
                'spi': ['Fin', 'Inicio'],
                'register': '52',
                'description': '{} fallo de tensión de medida en fase 3'
            },
        },
    7: {
        2: {
            'spi': False,
            'register': '53',
            'description': 'desincronización (el contador del punto de medida asociado se encuentra \ndesincronizado con respecto a su RM con una diferencia de tiempo significativa).'
        },
        9: {
            'spi': False,
            'register': '53',
            'description': 'cambio de hora, hora anterior'
        },
        11: {
            'spi': False,
            'register': '53',
            'description': 'cambio de hora, hora nueva'
        },
        21: {
            'spi': False,
            'register': '131',
            'description': 'Cierre de facturación por comando del Contrato I'
        },
        22: {
            'spi': False,
            'register': '132',
            'description': 'Cierre de facturación por comando del Contrato II'
        },
        23: {
            'spi': False,
            'register': '133',
            'description': 'Cierre de facturación por comando del Contrato III'
        },
    },
    15: {
            0: {
                'spi': False,
                'register': '54',
                'description': 'cambio de parámetros'
            },
            1: {
                'spi': False,
                'register': '54',
                'description': 'Cambio de alguna característica de los puertos de comunicaciones realizada por comando'
            },
            21: {
                'spi': False,
                'register': '131',
                'description': 'Cambio de parámetros del Contrato I'
            },
            22: {
                'spi': False,
                'register': '132',
                'description': 'Cambio de parámetros del Contrato II'
            },
            23: {
                'spi': False,
                'register': '133',
                'description': 'Cambio de parámetros del Contrato III'
            },
            24: {
                'spi': False,
                'register': '131',
                'description': 'Cambio de potencia de contrato (activo o latente) I por comando'
            },
            25: {
                'spi': False,
                'register': '132',
                'description': 'Cambio de potencia de contrato (activo o latente) II por comando'
            },
            26: {
                'spi': False,
                'register': '133',
                'description': 'Cambio de potencia de contrato (activo o latente) III por comando'
            },
            27: {
                'spi': False,
                'register': '131',
                'description': 'Cambio de la tabla de días festivos contrato I por comando'
            },
            28: {
                'spi': False,
                'register': '132',
                'description': 'Cambio de la tabla de días festivos contrato II por comando'
            },
            29: {
                'spi': False,
                'register': '133',
                'description': 'Cambio de la tabla de días festivos contrato III por comando'
            },
        },
    16: {
            0: {
                'spi': False,
                'register': '130',
                'description': 'Cambio de la Clave Privada del registrador'
            },
    },
    18: {
            1: {
                'spi': False,
                'register': '128',
                'description': 'incidencia de intrusismo'
            },
            2: {
                'spi': ['Fin', 'Inicio'],
                'register': '129',
                'description': '{} establecimiento de comunicaciones con un CM - llamada -'
            },
            3: {
                'spi': ['Fin', 'Inicio'],
                'register': '129',
                'description': '{} establecimiento de comunicaciones con el TPL'
            },
            4: {
                'spi': ['Recuperación', 'Pérdida'],
                'register': '129',
                'description': '{} de comunicación con el GPS'
            },
            21: {
                'spi': False,
                'register': '131',
                'description': 'Establecimiento de comunicaciones para Contrato I, producido al enviar el primer \nASDU con tal información dentro de cada sesión con un punto de medida'
            },
            22: {
                'spi': False,
                'register': '132',
                'description': 'Establecimiento de comunicaciones para Contrato II, producido al enviar el primer \nASDU con tal información dentro de cada sesión con un punto de medida'
            },
            23: {
                'spi': False,
                'register': '133',
                'description': 'Establecimiento de comunicaciones para Contrato III, producido al enviar el primer \nASDU con tal información dentro de cada sesión con un punto de medida'
            },
        },
    # '19': {
    #     '1-217': {
    #         'spi': False,
    #         'register': '55',
    #         'description': 'código de error interno, dependiente del fabricante'
    #     }
    # },
}


def get_event_description(event):
    '''
    Gets SingleEvent structure and returns text
    :param event: SingleEvent named tuple (SPA, SPQ, SPI, date)
    :return: text
    '''
    if not TM_EVENTS_DICT.get(event.SPA, False):
        txt = 'Código de error interno, dependiente del fabricante'
    else:
        ev_data = TM_EVENTS_DICT[event.SPA].get(event.SPQ)
        if ev_data:
            tmpl = ev_data.get('description')
            if ev_data.get('spi', False):
                txt = tmpl.format(ev_data.get('spi')[event.SPI])
            else:
                txt = tmpl
        else:
            txt = 'Código de error desconocido'

    return txt
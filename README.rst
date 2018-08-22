iec870ree
=========

.. image:: https://travis-ci.com/gisce/iec870ree.svg?branch=master
    :target: https://travis-ci.com/gisce/iec870ree   

.. image:: https://coveralls.io/repos/github/gisce/iec870ree/badge.svg?branch=master
    :target: https://coveralls.io/github/gisce/iec870ree?branch=master

	     

IEC-870-5-102 for REE Spanish Electric meters

Documentation about this protocol:

- `Initial definition <http://www.ree.es/sites/default/files/01_ACTIVIDADES/Documentos/Documentacion-Simel/protoc_RMCM10042002.pdf>`_
- `Extension <http://www.ree.es/sites/default/files/01_ACTIVIDADES/Documentos/Documentacion-Simel/AMPLIACION%20DEL%20PROTOCOLO%20Fase%202%202003-02-10.pdf>`_


Installation
------------

.. code-block::

    $ pip install iec870ree


Configuration of devices:

- `GSM <http://www.ree.es/sites/default/files/01_ACTIVIDADES/Documentos/Documentacion-Simel/Simel_gsm_v1.0.pdf>`_
- `RTC <http://www.ree.es/sites/default/files/01_ACTIVIDADES/Documentos/Documentacion-Simel/Simel_rtc_v1.0.pdf>`_


Implemented ASDUs 
-----------------

- C_AC_NA_2: Autentificación
- C_CI_NU_2:  Leer incrementales absolutos
- M_IT_TG_2: Respuesta  Leer incrementales absolutos
- C_CI_NT_2: Leer totales absolutos
- M_IT_TK_2: Respuesta de C_CI_NT_2
- C_FS_NA_2: Finalizar sesión
- C_TI_NA_2:  Leer fecha y hora actuales
- M_TI_TA_2: Respuesta Fecha y hora actuales
- C_RD_NA_2: Leer identificador de fabricante y equipo
- P_MP_NA_2: Respuesta Identificador del fabricante y equipo
- C_TA_VC_2: Leer Información de Tarificación (Valores en Curso)
- M_TA_VC_2: Respuesta Información de Tarificación (Valores en Curso)
- C_TA_VM_2: Leer Información de Tarificación (Valores Memorizados)
- M_TA_VM_2: Respuesta Información de Tarificación (Valores Memorizados)
- C_CB_UN_2 (opcional): Similar a C_CI_NU_2 y C_CI_NT_2
- M_IB_TK_2: Respuesta de C_CB_UN_2

History of this project
-----------------------

Initial project was writed by `Javier de la Puente <https://github.com/javierdelapuente>`_ and was called `reeprotocol <https://github.com/javierdelapuente/reeprotocol>`_ then at `GISCE-TI <https://gisce.net>`_ started working on it and implement `Ip Layer <https://github.com/javierdelapuente/reeprotocol/pull/1>`_, `base changes <https://github.com/javierdelapuente/reeprotocol/pull/8>`_ and `new ASDUs <https://github.com/javierdelapuente/reeprotocol/pull/9>`_. And we put this library in production :rocket:! and our speed was different of the main repo. Then we start a new project forked from the original. You can see the `issue with the history <https://github.com/javierdelapuente/reeprotocol/issues/10>`_

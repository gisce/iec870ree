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

- C_AC_NA_2: Authentication (Already implemented on origin)
- C_CI_NU_2: Read integrated totals **incremental** values (Already implemented on origin)
- M_IT_TK_2: Answer to C_CI_NU_2 (Already implemented on origin)
- C_CI_NT_2: Read integrated totals **absolute** values
- M_IT_TG_2: Answer to C_CI_NT_2
- C_FS_NA_2: Finish session (Already implemented on origin)
- C_TI_NA_2: Read current date and time
- M_TI_TA_2: Answer to C_TI_NA_2
- C_RD_NA_2: Read manufacturer and device identifiers
- P_MP_NA_2: Answer to C_RD_NA_2
- C_TA_VC_2: Read metering information **Current values**
- M_TA_VC_2: Answer to C_TA_VC_2
- C_TA_VM_2: Read metering information **Saved values**
- M_TA_VM_2: Answer to C_TA_VM_2
- C_CB_UN_2: (optional) Read integrated totals **incremental** values. With blocks choices. Similar to C_CI_NU_2.
- M_IB_TK_2: Answer to C_CB_UN_2
- C_CS_TA_2: Set date and time of meter (sincro). Use this ASDU as a response
- C_PC_NA_2: Read contracted powers
- M_PC_NA_2: Answer to C_PC_NA_2

History of this project
-----------------------

Initial project was writen by `Javier de la Puente <https://github.com/javierdelapuente>`_
and was called `reeprotocol <https://github.com/javierdelapuente/reeprotocol>`_ .
Then `GISCE-TI <https://gisce.net>`_ started working on it and implemented
`Ip Layer <https://github.com/javierdelapuente/reeprotocol/pull/1>`_,
`base changes <https://github.com/javierdelapuente/reeprotocol/pull/8>`_
and `new ASDUs <https://github.com/javierdelapuente/reeprotocol/pull/9>`_.
With that we put this library in production 🚀! Our working speed was different
from the main repo pace so we started a new project forked from the original.
You can see the issue with the history `here <https://github.com/javierdelapuente/reeprotocol/issues/10>`_.

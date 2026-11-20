Circular Log
============

Read the Circular log document in ``gp_docs`` before going through this document.
``CircularLog`` class is the base class for ``LoadSurveyReader`` and ``LoadSurveyReader``. All these classes are implemented in ``gp_node.network.circular_log``. The **LogApp** and **LoadSurveyApp** in node_fw firmware store the log and load survey in the external flash memory. Their corresponding analog in the python world are ``LoadSurveyReader`` class and ``LogReader`` class. Since the data is stored in the external flash memory, ``FlashIO`` protocol is used to directly read the meta data and also to read the entries from *raw* hex data fetched from the external flash memory.

The Python implementation of ``CircularLog`` understands the structure of meta data of data buffers as given in the pdf document in ``gp_docs``. Hence, ``FlashIO`` protocol is used to read the flash memory contents directly, and then the python implementation makes sense of the entries using the meta data.

Tutorial
--------

Some of the ``node-shell`` commands use the classes ``LogReader``, ``LoadSurveyReader``. The table shown below matches the ``node-shell`` commands with their corresponding functions in ``circular_log``. Note that ``CircularLog`` is the base class for ``LogReader`` and ``LoadSurveyReader``.

.. graphviz::

   digraph foo {
      "CircularLog" -> "LogReader";
      "CircularLog" -> "LoadSurveyReader";
   }


+---------------------+-----------------------------------------+
|  node-shell command |             Python function             |
+=====================+=========================================+
| log_print_direct    | LogReader.print_log_from_node           |
+---------------------+-----------------------------------------+
| log_header          | CircularLog.dump_header_to_file         |
+---------------------+-----------------------------------------+
| log_dump_bin        | CircularLog.dump                        |
+---------------------+-----------------------------------------+
| log_print_bin       | LogReader.print_log_from_bin            |
+---------------------+-----------------------------------------+
| survey_print_direct | LoadSurveyReader.print_survey_from_node |
+---------------------+-----------------------------------------+
| survey_header       | CircularLog.dump_header_to_file         |
+---------------------+-----------------------------------------+
| survey_dump_bin     | CircularLog.dump                        |
+---------------------+-----------------------------------------+
| survey_print_bin    | LoadSurveyReader.print_survey_from_bin  |
+---------------------+-----------------------------------------+


API
---	               

.. autoclass:: gp_node.network.circular_log.circular_log.CircularLog
   :members:

.. autoclass:: gp_node.network.circular_log.load_survey.LoadSurveyReader
   :members:

.. autoclass:: gp_node.network.circular_log.log_reader.LogReader
   :members:

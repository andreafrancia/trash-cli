# Copyright (C) 2007-2023 Andrea Francia Trivolzio(PV) Italy
import logging

my_logger = logging.getLogger('trashcli.trash')
my_logger.setLevel(logging.WARNING)
my_logger.addHandler(logging.StreamHandler())

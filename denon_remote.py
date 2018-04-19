# -*- coding: utf-8 -*-
import binascii
import serial
import time
import logging


class DenonRemote(object):
    """Controller for Denon 2307CI Audio/Video receiver

    This controller sends queries and commands to a Denon 2307CI receiver over
    RS232.  

    Attributes:
        port_name: A string name of serial port to use for communicating with
            the TV.  Example: 'COM3'
        baud_rate: An integer specifying the baud rate of the serial port.
            Defaults to 9600, the setting for the Denon 2307CI.
        log_level: A standard Python logging class log level.
    """

    def __init__(self, port_name, log_level=logging.ERROR, baud_rate=9600):
        """Initializes with the given settings.

        Args:
            port_name: A string containing the serial port name
            log_level: A Python logging log level
            baud_rate: A baud rate for the serial port
        """
        self.init_logging(log_level)

        self.port_name = port_name
        self.baud_rate = baud_rate

    def open(self):
        """Configures and opens the serial port
        """
        self.logger.debug('opening %s', self.port_name)

        self.port = serial.Serial()
        self.port.baudrate = self.baud_rate
        self.port.port = self.port_name
        self.port.open()

    def close(self):
        """Closes the serial port
        """
        self.logger.debug('closing %s', self.port_name)

        self.port.close()

    def query(self, query):
        """Sends the given query to the receiver and reads the response

        Args:
            query: A string with the command characters to send

        Returns:
            The response string (max length 135) from the receiver
        """
        if self.port.isOpen() == False:
            self.logger.error('Tried to send a command but port wasn\'t open')
            return

        self.port.write('{}?\r'.format(query))

        # keep reading until we either hit the carriage return or 135 bytes
        while True:
            resp = self.port.read_until(terminator='\r', size=135)
            break

        return resp

    def command(self, command):
        """Sends the given command to the receiver

        Args:
            command: A string with the command characters to send. These commands
            are comprised of a two character identifier followed by a string with
            an argument pertaining to the identifier.
        """
        if self.port.isOpen() == False:
            self.logger.error('Tried to send a command but port wasn\'t open')
            return

        self.port.write('{}\r'.format(command))

    def power_off(self):
        self.logger.info('powering off')
        self.command('PWSTANDBY')

    def power_on(self):
        self.logger.info('powering on')
        self.command('PWON')

    def query_power(self):
        self.logger.info('querying power status')
        self.logger.info('power: {}'.format(self.query('PW')))

    def query_volume(self):
        self.logger.info('querying volume status')
        self.logger.info('volume: {}'.format(self.query('MV')))

    def set_volume(self, volume_level):
        """Set volume level of Denon receiver, given a percentage

        Args:
            volume_level: Desired volume as a percentage of the maximum

        Note, the actual volume level is a setting corresponding to
        a negative decibel rating.  Testing showed the following settings
        given a high powered external amplifier with relatively large
        speakers:

            70 == -10.0dB way too loud, but maybe for some movies
            65 == -15.0dB loudest reasonable volume
            25 == -55.0dB lowest reasonable volume
        """
        max_volume = 65
        min_volume = 25

        # calculating new volume as a percentage between min and max
        new_volume = volume_level * \
            (max_volume - min_volume) / 100 + min_volume

        # safety check
        if new_volume > max_volume:
            self.logger.error(
                'calculated volume setting above max volume level: %d', new_volume)
            return

        self.logger.info('setting volume to %d%% (MV%d)',
                         volume_level, new_volume)

        self.command('MV{}'.format(new_volume))

    def query_source(self):
        self.logger.info('querying input source')
        self.logger.info('source: {}'.format(self.query('SI')))

    def set_source(self, source_name):
        """Set source input, given the source name

        Args:
            source_name: String of the desired source name.  Valid sources for
            the Denon 2307CI are: TV, DVD, TUNER, CD, VCR-1, VCR-2, PHONO, 
            V.AUX, CDR/TAPE.
        """
        self.logger.info('setting source to %s', source_name)
        self.command('SI{}'.format(source_name))

    def init_logging(self, log_level):
        """Initialize logging for the remote

        Args:
            log_level: A enum which can be DEBUG, INFO, WARNING, ERROR,
                or CRITICAL.  Example: logging.INFO
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(log_level)
        formatter = logging.Formatter('%(asctime)s %(name)s [%(levelname)s] '
                                      '%(message)s')
        ch = logging.StreamHandler()
        ch.setLevel(log_level)
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        self.logger.debug('logging initialized')

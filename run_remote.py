#!/usr/bin/env python

"""Runner script for DenonRemote

This script provides an interface to the DenonRemote module for
use in directly controlling a Denon 2307CI or similar receiver
over RS232.
"""

import argparse
import logging
from denon_remote import DenonRemote


def volume_command(remote, args):
    if args.query:
        remote.query_volume()
        return

    if args.level is not None:
        remote.set_volume(args.level)


def power_command(remote, args):
    if args.query:
        remote.query_power()
        return

    if args.power == 'ON':
        remote.power_on()
    elif args.power == 'OFF':
        remote.power_off()


def source_command(remote, args):
    if args.query:
        remote.query_source()
        return

    remote.set_source(args.source)


def main():
    parser = argparse.ArgumentParser(
        description='Runner script for Denon Remote')
    parser.add_argument('-p', '--port', dest='port', type=str, default='COM4',
                        help='Serial port to communication with the device on')
    parser.add_argument('-q', '--query', action='store_true',
                        help='Query the current status of the given command')
    parser.add_argument('-v', '--verbosity', dest='verbosity', choices=[
        'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'], default='ERROR', help='Set the verbosity level (default=ERROR)')

    sub_parser = parser.add_subparsers()

    sp_volume = sub_parser.add_parser('volume', help='Volume functions')
    sp_volume.add_argument('-l', '--level', dest='level', type=int,
                           help='Volume level of the device as a percentage of the maximum')

    sp_power = sub_parser.add_parser('power', help='Power functions')
    sp_power.add_argument(metavar='P', dest='power', nargs='?', default='ON',
                          choices=['ON', 'OFF'], help='Power the device on or off')

    sp_source = sub_parser.add_parser('source', help='Source functions')
    sp_source.add_argument(metavar='S', dest='source', choices=[
                           'TV', 'DVD', 'TUNER', 'CD', 'VCR-1', 'VCR-2', 'PHONO', 'V.AUX', 'CDR/TAPE'],
                           nargs='?', default='TV',
                           help='Select the input source')

    sp_volume.set_defaults(func=volume_command)
    sp_power.set_defaults(func=power_command)
    sp_source.set_defaults(func=source_command)

    args = parser.parse_args()

    remote = DenonRemote(args.port, log_level=getattr(logging, args.verbosity))
    remote.open()

    args.func(remote, args)

    remote.close()


if __name__ == '__main__':
    main()

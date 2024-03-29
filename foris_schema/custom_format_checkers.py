# foris-schema
# Copyright (C) 2018 CZ.NIC, z.s.p.o. <http://www.nic.cz>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


import re
import socket
import struct

from jsonschema import FormatChecker
from jsonschema import _format as existing_checkers


MAC_RE = r"^([a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}$"

format_checker = FormatChecker()


@format_checker.checks("ipv4netmask", (socket.error, TypeError))
def check_ipv4netmask(value):
    addr = socket.inet_aton(value)
    addr_int = struct.unpack(">I", addr)[0]
    bin_repr = "{:032b}".format(addr_int)
    if "0" in bin_repr.rstrip("0"):
        return False
    else:
        return True


@format_checker.checks("ipv4prefix", (socket.error, ValueError, AttributeError))
def check_ipv4prefix(value):
    address, prefix = value.rsplit("/", 1)
    prefix_num = int(prefix)
    return existing_checkers.is_ipv4(address) and 0 <= prefix_num and prefix_num <= 32


@format_checker.checks("ipv6prefix", (socket.error, ValueError, AttributeError))
def check_ipv6prefix(value):
    address, prefix = value.rsplit("/", 1)
    prefix_num = int(prefix)
    return existing_checkers.is_ipv6(address) and 0 <= prefix_num and prefix_num <= 128


@format_checker.checks("macaddress", (ValueError, TypeError))
def check_macaddress(value):
    return True if re.match(MAC_RE, value) else False

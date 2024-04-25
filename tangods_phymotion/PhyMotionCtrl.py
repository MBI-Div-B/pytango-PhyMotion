#!/usr/bin/python3 -u
# coding: utf8
# PhyMotionCtrl

from tango import DevState
from tango.server import Device, command, device_property
import socket


class PhyMotionCtrl(Device):
    # device properties
    Address = device_property(
        dtype="str",
        default_value="phymotion.lab",
    )

    Port = device_property(
        dtype="int",
        default_value=22222,
    )

    # definition some constants
    __STX = chr(2)  # Start of text
    __ACK = chr(6)  # Command ok
    __NACK = chr(0x15)  # command failed
    __ETX = chr(3)  # end of text

    def init_device(self):
        super().init_device()
        self.set_state(DevState.INIT)
        self.info_stream("init_device()")

        # open socket connection
        self.con = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.con.connect((self.Address, self.Port))
            self.info_stream("Connected to {:s}:{:d}".format(self.Address, self.Port))
            self.set_state(DevState.ON)
        except Exception:
            self.error_stream(
                "Failed to open {:s}:{:d}".format(self.Address, self.Port)
            )
            self.set_state(DevState.FAULT)

    def delete_device(self):
        self.con.close()
        self.set_state(DevState.OFF)

    @command(dtype_in=str, dtype_out=str)
    def write_read(self, cmd):
        """
        see phymotion reference for command syntax (page 12)
        address is always 0 (except for rotary switch)
        then the command follows
        :XX is the flag to skip the checksum-verify
        """
        cmd = self.__STX + "0" + cmd + ":XX" + self.__ETX
        self.debug_stream("write command: {:s}".format(cmd))
        self.con.send(cmd.encode("utf-8"))
        res = self.con.recv(1024).decode("utf-8")
        self.debug_stream("read response: {:s}".format(res))
        if self.__ACK in res:
            return (
                res.lstrip(self.__STX)
                .lstrip(self.__ACK)
                .rstrip(self.__ETX)
                .split(":")[0]
            )
        else:
            # no acknowledgment in response
            return self.__NACK

    @command
    def dump_to_eprom(self):
        self.write_read("SA")

    def is_write_allowed(self):
        if self.get_state() in [DevState.FAULT, DevState.OFF]:
            return False
        return True


if __name__ == "__main__":
    PhyMotionCtrl.run_server()

#!/usr/bin/python3 -u
# coding: utf8
# PhyMotionAxis

from tango import Database, DevFailed, AttrWriteType, DevState
from tango import DeviceProxy, DispLevel
from tango.server import device_property
from tango.server import Device, attribute, command
import time


_MOVEMENT_UNITS = [
    "steps",
    "mm",
    "inch",
    "degree"
]

_PHY_AXIS_STATUS_CODES = [
    "Axis busy",  # 0
    "Command invalid",  # 1
    "Axis waits for synchronisation",  # 2
    "Axis initialised",  # 3
    "Axis limit+ switch",  # 4
    "Axis limit- switch",  # 5
    "Axis limit center switch",  # 6
    "Axis limit+ software switch",  # 7
    "Axis limit- software switch",  # 8
    "Axis power stage is ready",  # 9
    "Axis is in the ramp",  # 10
    "Axis internal error",  # 11
    "Axis limit switch error",  # 12
    "Axis power stage error",  # 13
    "Axis SFI error",  # 14
    "Axis ENDAT error",  # 15
    "Axis is running",  # 16
    "Axis is in recovery time (s. parameter P13 or P16)",  # 17
    "Axis is in stop current delay time (parameter P43)",  # 18
    "Axis is in position",  # 19
    "Axis APS is ready",  # 20
    "Axis is positioning mode",  # 21
    "Axis is in free running mode",  # 22
    "Axis multi F run",  # 23
    "Axis SYNC allowed",  # 24
]


class PhyMotionAxis(Device):
    # device properties
    CtrlDevice = device_property(dtype="str", default_value="domain/family/member")

    Axis = device_property(
        dtype="int16", default_value=1, doc="Module number in controller (starts at 1)."
    )

    TimeOut = device_property(
        dtype="float",
        default_value=0.2,
        doc=(
            "Timeout in seconds between status requests\n"
            "to reduce communication traffic."
        ),
    )

    # device attributes
    sw_limit_minus = attribute(
        dtype="float",
        format="%8.3f",
        label="SW limit - position",
        unit="steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    sw_limit_plus = attribute(
        dtype="float",
        format="%8.3f",
        label="SW limit + position",
        unit="steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    position = attribute(
        dtype="float",
        format="%8.3f",
        label="position",
        unit="steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.OPERATOR,
    )

    last_position = attribute(
        dtype="float",
        format="%8.3f",
        label="last position",
        unit="steps",
        memorized=True,
        hw_memorized=True,
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    inverted = attribute(
        dtype="bool",
        label="inverted",
        memorized=True,
        hw_memorized=True,
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    acceleration = attribute(
        dtype="float",
        format="%8.3f",
        label="acceleration",
        unit="steps/s\u0032",
        min_value=4000,
        max_value=500000,
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    velocity = attribute(
        dtype="float",
        format="%8.3f",
        label="velocity",
        unit="steps/s",
        min_value=0,
        max_value=40000,
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    homing_velocity = attribute(
        dtype="float",
        format="%8.3f",
        label="homing velocity",
        unit="steps/s",
        min_value=0,
        max_value=40000,
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    hold_current = attribute(
        dtype="float",
        label="hold current",
        unit="A",
        min_value=0,
        max_value=6.5,
        format="%3.2f",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc=(
            "I1AM01: 0 to 2.50 A_rms\n"
            "I1AM02: 0 to 3.50 A_rms\n"
            "I1AM02 LPS: 0 to 6.50 A_rms\n"
        ),
    )

    run_current = attribute(
        dtype="float",
        label="run current",
        unit="A",
        min_value=0,
        max_value=6.5,
        format="%3.2f",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc=(
            "I1AM01: 0 to 2.50 A_rms\n"
            "I1AM02: 0 to 3.50 A_rms\n"
            "I1AM02 LPS: 0 to 6.50 A_rms\n"
        ),
    )

    limit_switch_type = attribute(
        dtype="DevEnum",
        enum_labels=[
            "NCC NCC NCC",
            "NCC NCC NOC",
            "NOC NCC NCC",
            "NOC NCC NOC",
            "NCC NOC NCC",
            "NCC NOC NOC",
            "NOC NOC NCC",
            "NOC NOC NOC"
            ],
        label="limit switch type",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc=("NOC or NCC for limit-, reference/center, limit+"),
    )

    steps_per_unit = attribute(
        dtype="float",
        format="%10.1f",
        label="steps per unit",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    step_resolution = attribute(
        dtype="DevEnum",
        enum_labels=[
            "1/1",
            "1/2",
            "1/2.5",
            "1/4",
            "1/5",
            "1/8",
            "1/10",
            "1/16",
            "1/20",
            "1/32",
            "1/64",
            "1/128",
            "1/256",
            ],
        label="step resolution",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    backlash_compensation = attribute(
        dtype="float",
        format="%8.3f",
        label="backlash compensation",
        unit="steps",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
    )

    type_of_movement = attribute(
        dtype="DevEnum",
        enum_labels=[
            "rotational",
            "linear hw limit",
            "linear sw limit",
            "linear hw+sw limit"
        ],
        label="type of movement",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc=(
            "0 = rotation; limit switches are ignored.\n"
            "1 = linear; only hardware limit switches monitored.\n"
            "2 = linear; only software limit switches monitored.\n"
            "3 = linear; hardware and software limit switches monitored."
        ),
    )

    movement_unit = attribute(
        dtype="DevEnum",
        enum_labels=_MOVEMENT_UNITS,
        label="unit",
        access=AttrWriteType.READ_WRITE,
        display_level=DispLevel.EXPERT,
        doc="Allowed unit values are steps, mm, inch, degree",
    )

    # private class properties
    __NACK = chr(0x15)  # command failed

    # decorators
    def update_parameters(func):
        """update_parameters

        decorator for setter-methods of attributes in order to update
        the values of all parameters/attributes of the DS.
        """

        def inner(self, value):
            func(self, value)
            self.read_all_parameters()

        return inner

    def init_device(self):
        super().init_device()
        self.info_stream("init_device()")        
        self.set_state(DevState.INIT)
        self.info_stream("module axis: {:d}".format(self.Axis))

        try:
            self.ctrl = DeviceProxy(self.CtrlDevice)
            self.info_stream("ctrl. device: {:s}".format(self.CtrlDevice))
        except DevFailed as df:
            self.error_stream("failed to create proxy to {:s}".format(df))
            self.set_state(DevState.FAULT)
            return

        self._last_status_query = 0
        self._statusbits = 25 * [0]
        self._inverted = False

        # read all parameters
        self.read_all_parameters()
        # update units and formatting
        self.set_display_unit(
            unit=_MOVEMENT_UNITS[int(self._all_parameters['P02R'])-1],
            steps_per_unit=1/float(self._all_parameters['P03R'])
        )

        self.set_state(DevState.ON)

    def delete_device(self):
        self.set_state(DevState.OFF)

    def _decode_status(self, status, ndigits):
        """Decode status number to bit list.

        Status codes are returned as decimal, but should be interpreted
        as hex representation of packed 4-bit nibbles. In other words, the
        decimal status code needs to be formatted as a hexadecimal number,
        where each hex digit represents 4 status bits.
        To get the correct bit status length, leading zeros are required.
        Hence the maximum number of digits must be provided as a parameter.

        Documentation:
        https://www.phytron.de/fileadmin/user_upload/produkte/endstufen_controller/pdf/phylogic-de.pdf
        page 41
        """
        hexstring = f"{int(status):0{ndigits}X}"
        statusbits = []
        for digit in hexstring[::-1]:
            digit_num = int(digit, base=16)
            statusbits += [(digit_num >> i) & 1 for i in range(4)]
        return statusbits

    def always_executed_hook(self):
        # axis state query takes 10 ms (per axis!) on phymotion over TCP
        # -> limit max. query rate to 5 Hz
        now = time.time()
        if now - self._last_status_query > self.TimeOut:
            status, position = self.send_cmd(["SE", "P20R"])
            self.debug_stream(f"position: {position}")
            self._last_status_query = now
            self._statusbits = self._decode_status(int(status), 7)
            self.debug_stream(f"status bits: {self._statusbits}")
            # set current position
            self._all_parameters["P20R"] = position

            status_list = []
            for n, bit_value in enumerate(self._statusbits):
                if bit_value:
                    if (n == 4 or n == 7) and self._inverted:
                        status_list.append(_PHY_AXIS_STATUS_CODES[n + 1])
                    elif (n == 5 or n == 8) and self._inverted:
                        status_list.append(_PHY_AXIS_STATUS_CODES[n - 1])
                    else:
                        status_list.append(_PHY_AXIS_STATUS_CODES[n])
            self.set_status("\n".join(status_list))

            if any([self._statusbits[n] for n in [12]]):
                # reset limit switch error on module
                self.reset_errors()

            if any([self._statusbits[n] for n in [3, 19]]):
                self.set_state(DevState.ON)

            if any([self._statusbits[n] for n in [0, 16, 21, 22, 23]]):
                self.set_state(DevState.MOVING)
            elif (
                any([self._statusbits[n] for n in [4, 5, 6, 7, 8, 12]])
                and int(self._all_parameters["P01R"]) > 0
            ):
                # no alarm for rotational stages
                self.set_state(DevState.ALARM)
            elif any([self._statusbits[n] for n in [1, 11, 13, 14, 15]]):
                self.set_state(DevState.FAULT)

    # attribute read/write methods
    def read_sw_limit_minus(self):
        if self._inverted:
            return -1 * float(self._all_parameters["P23R"])
        else:
            return float(self._all_parameters["P24R"])

    @update_parameters
    def write_sw_limit_minus(self, value):
        if self._inverted:
            self.send_cmd("P23S{:f}".format(-1 * value))
        else:
            self.send_cmd("P24S{:f}".format(value))

    def read_sw_limit_plus(self):
        if self._inverted:
            return -1 * float(self._all_parameters["P24R"])
        else:
            return float(self._all_parameters["P23R"])

    @update_parameters
    def write_sw_limit_plus(self, value):
        if self._inverted:
            self.send_cmd("P24S{:f}".format(-1 * value))
        else:
            self.send_cmd("P23S{:f}".format(value))

    def read_position(self):
        ret = float(self._all_parameters["P20R"])
        if self._inverted:
            return -1 * ret
        else:
            return ret

    def write_position(self, value):
        memorize_value = value
        if self._inverted:
            value = -1 * value
        answer = self.send_cmd("A{:.10f}".format(value))
        if answer != self.__NACK:
            self.set_state(DevState.MOVING)
            DeviceProxy(self.get_name()).write_attribute(
                "last_position", memorize_value
            )

    def read_last_position(self):
        return self._last_position

    def write_last_position(self, value):
        self._last_position = value

    def read_inverted(self):
        return self._inverted

    def write_inverted(self, value):
        self._inverted = bool(value)

    def read_acceleration(self):
        return int(self._all_parameters["P15R"])*float(self._all_parameters["P03R"])

    @update_parameters
    def write_acceleration(self, value):
        acceleration = int(value/float(self._all_parameters["P03R"]))
        self.send_cmd("P15S{:d}".format(acceleration))

    def read_velocity(self):
        return int(self._all_parameters["P14R"])*float(self._all_parameters["P03R"])

    @update_parameters
    def write_velocity(self, value):
        velocity = int(value/float(self._all_parameters["P03R"]))
        self.send_cmd("P14S{:d}".format(velocity))

    def read_homing_velocity(self):
        return int(self._all_parameters["P08R"])*float(self._all_parameters["P03R"])

    @update_parameters
    def write_homing_velocity(self, value):
        velocity = int(value/float(self._all_parameters["P03R"]))
        self.send_cmd("P08S{:d}".format(velocity))

    def read_run_current(self):
        return float(self._all_parameters["P41R"]) / 100

    @update_parameters
    def write_run_current(self, value):
        value = int(value * 100)
        self.send_cmd("P41S{:d}".format(value))

    def read_hold_current(self):
        return float(self._all_parameters["P40R"]) / 100

    @update_parameters
    def write_hold_current(self, value):
        value = int(value * 100)
        self.send_cmd("P40S{:d}".format(value))

    def read_limit_switch_type(self):
        return int(self._all_parameters["P27R"])

    @update_parameters
    def write_limit_switch_type(self, value):
        self.send_cmd("P27S{:d}".format(int(value)))

    def read_steps_per_unit(self):
        # inverse of spindle pitch (see manual page 77)
        return 1 / float(self._all_parameters["P03R"])

    @update_parameters
    def write_steps_per_unit(self, value):
        # inverse of spindle pitch (see manual page 77)
        self.send_cmd("P03S{:10.8f}".format(1/value))
        self.set_display_unit(
            unit=_MOVEMENT_UNITS[int(self._all_parameters['P02R'])-1],
            steps_per_unit=value
            )

    def read_step_resolution(self):
        return int(self._all_parameters["P45R"])

    @update_parameters
    def write_step_resolution(self, value):
        if value not in range(14):
            raise ValueError(f"Invalid step resolution index: {value} not in (0-12)")
        self.send_cmd("P45S{:d}".format(value))

    def read_backlash_compensation(self):
        ret = float(self._all_parameters["P25R"])
        if self._inverted:
            return -1 * ret
        else:
            return ret

    @update_parameters
    def write_backlash_compensation(self, value):
        if self._inverted:
            value = -1 * value
        self.send_cmd("P25S{:f}".format(float(value)))

    def read_type_of_movement(self):
        return int(self._all_parameters["P01R"])

    @update_parameters
    def write_type_of_movement(self, value):
        self.send_cmd("P01S{:d}".format(int(value)))

    def read_movement_unit(self):
        return int(self._all_parameters["P02R"])-1

    @update_parameters
    def write_movement_unit(self, value):
        self.send_cmd("P02S{:d}".format(int(value) + 1))
        self.set_display_unit(
            unit=_MOVEMENT_UNITS[value],
            steps_per_unit=1/float(self._all_parameters['P03R'])
            )

    # internal methods
    def set_display_unit(self, unit="", steps_per_unit=0):
        attributes = [
            "position",
            "last_position",
            "sw_limit_minus",
            "sw_limit_plus",
            "backlash_compensation",
            "velocity",
            "homing_velocity",
            "acceleration",
        ]
        for attr in attributes:
            ac3 = self.get_attribute_config_3(attr)
            if attr == "velocity" or attr == "homing_velocity":
                unit_set = unit + "/s"
                ac3[0].min_value = str(0)
                ac3[0].max_value = str(40000 / steps_per_unit)
            elif attr == "acceleration":
                unit_set = unit + "/s\u0032"
                ac3[0].min_value = str(4000 / steps_per_unit)
                ac3[0].max_value = str(500000 / steps_per_unit)
            else:
                unit_set = unit
            ac3[0].unit = unit_set.encode("utf-8")

            if (1 / steps_per_unit % 1) == 0.0:
                ac3[0].format = "%8d"
            else:
                ac3[0].format = "%8.3f"
            self.set_attribute_config_3(ac3)

    def _send_cmd(self, cmd_str):
        # add module address to beginning of command
        if isinstance(cmd_str, list):
            cmd = ""
            for sub_cmd in cmd_str:
                cmd = cmd + " " + "{:d}.1{:s}".format(self.Axis, sub_cmd)
            res = self.ctrl.write_read(cmd).split(chr(6))
        else:
            cmd = "{:d}.1{:s}".format(self.Axis, cmd_str)
            res = self.ctrl.write_read(cmd)
        if res == self.__NACK:
            self.set_state(DevState.FAULT)
            self.warn_stream(
                "command not acknowledged from controller " "-> Fault State"
            )
            return ""
        return res

    # commands
    @command(
        dtype_in=str, dtype_out=str, doc_in="enter a command", doc_out="the response"
    )
    def send_cmd(self, cmd):
        return self._send_cmd(cmd)

    @command(dtype_in=float, doc_in="position")
    def set_position(self, value):
        if self._inverted:
            value = -1 * value
        self.send_cmd("P20S{:.4f}".format(value))

    @command()
    def restore_position(self):
        self.set_position(self._last_position)

    @command
    def jog_plus(self):
        if self._inverted:
            self.send_cmd("L-")
        else:
            self.send_cmd("L+")
        self.set_state(DevState.MOVING)

    @command
    def jog_minus(self):
        if self._inverted:
            self.send_cmd("L+")
        else:
            self.send_cmd("L-")
        self.set_state(DevState.MOVING)

    @command
    def homing_plus(self):
        if self._inverted:
            self.send_cmd("R-")
        else:
            self.send_cmd("R+")
        self.set_state(DevState.MOVING)

    @command
    def homing_minus(self):
        if self._inverted:
            self.send_cmd("R+")
        else:
            self.send_cmd("R-")
        self.set_state(DevState.MOVING)

    @command
    def stop(self):
        self.send_cmd("S")
        self.set_state(DevState.ON)

    @command
    def abort(self):
        self.send_cmd("SN")
        self.set_state(DevState.ON)

    @command
    def reset_errors(self):
        self.send_cmd("SEC")

    @command(dtype_out=str)
    def write_to_eeprom(self):
        self._send_cmd("SA")
        self.info_stream("parameters written to EEPROM")
        return "parameters written to EEPROM"

    @command()
    def read_all_parameters(self):
        self._all_parameters = {}
        # generate list of commands
        cmd_list = []
        for par in range(1, 59):
            cmd_str = "P{:02d}R".format(par)
            cmd_list.append(cmd_str)
        # query list of commands
        ret = self.send_cmd(cmd_list)
        # parse response
        for i, cmd_str in enumerate(cmd_list):
            self._all_parameters[cmd_str] = ret[i]

    @command(dtype_out=str)
    def dump_all_parameters(self):
        self.read_all_parameters()
        res = ""
        for par in range(1, 59):
            cmd = "P{:02d}R".format(par)
            res = res + "P{:02d}: {:s}\n".format(par, str(self._all_parameters[cmd]))
        return res


if __name__ == "__main__":
    PhyMotionAxis.run_server()

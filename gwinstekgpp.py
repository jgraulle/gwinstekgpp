#!/usr/bin/python3
import serial
import enum
import time


class Gwinstekgpp:
    class MeasureType(enum.Enum):
        VOLTAGE = 1
        CURRENT = 2
        POWER = 3
        ALL = 4

        def toSerialStr(self):
            return self.name[0:4]

    class SourceType(enum.Enum):
        VOLTAGE = 1
        CURRENT = 2
        RESISTOR = 3

        def toSerialStr(self) -> str:
            if self == Gwinstekgpp.SourceType.RESISTOR:
                return self.name[0:3]
            return self.name[0:4]

    class Ch1Ch2Mode(enum.Enum):
        POWER_INDEPENDENT = 1
        POWER_SERIES = 2
        POWER_PARALLEL = 3
        LOAD_CV = 4
        LOAD_CC = 5
        LOAD_CR = 6

        @staticmethod
        def fromSerialStr(mode: str) -> "Gwinstekgpp.Ch1Ch2Mode":
            if mode == "IND":
                return Gwinstekgpp.Ch1Ch2Mode.POWER_INDEPENDENT
            elif mode == "SER":
                return Gwinstekgpp.Ch1Ch2Mode.POWER_SERIES
            elif mode == "PAR":
                return Gwinstekgpp.Ch1Ch2Mode.POWER_PARALLEL
            elif mode == "CV":
                return Gwinstekgpp.Ch1Ch2Mode.LOAD_CV
            elif mode == "CC":
                return Gwinstekgpp.Ch1Ch2Mode.LOAD_CC
            elif mode == "CR":
                return Gwinstekgpp.Ch1Ch2Mode.LOAD_CR
            else:
                raise ValueError(f"Receive an unexpected CH1/CH2 mode {mode}")

    class Channel:
        def __init__(self, gwinstekgpp: "Gwinstekgpp", channel: int):
            self._gwinstekgpp = gwinstekgpp
            self._channel = channel

        def measure(self, measureType: "Gwinstekgpp.MeasureType") -> float|list[float]:
            """Return the given measure.
            When select ALL measure type return a list of 3 floats with first Voltage, second current
            and last power
            """
            self._gwinstekgpp._serial.write(f":MEAS{self._channel}:{measureType.toSerialStr()}?\r".encode())
            response = self._gwinstekgpp._serial.readline().strip()
            if measureType == Gwinstekgpp.MeasureType.ALL:
                return [float(x) for x in response.split(b',')]
            return float(response)

        @property
        def voltage(self) -> float:
            """Returns the actual output voltage."""
            self._gwinstekgpp._serial.write(f"VOUT{self._channel}?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip().removesuffix(b"V"))

        @property
        def current(self) -> float:
            """Returns the actual output current."""
            self._gwinstekgpp._serial.write(f"IOUT{self._channel}?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip().removesuffix(b"A"))

        @property
        def outputEnable(self) -> bool:
            """Get the actual output state."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:STAT?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"ON"

        @outputEnable.setter
        def outputEnable(self, value: bool):
            """Enable or disable the actual output state."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:STAT {"1" if value else "0"}\r".encode())

        @property
        def ovpEnable(self) -> bool:
            """Get the actual output over voltage protection state."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OVP:STAT?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"ON"

        @ovpEnable.setter
        def ovpEnable(self, value: bool):
            """Enable or disable the actual output over voltage protection state."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OVP:STAT {"1" if value else "0"}\r".encode())

        @property
        def ovpValue(self) -> float:
            """Get the actual output over voltage protection value."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OVP?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip())

        @ovpValue.setter
        def ovpValue(self, value: float):
            """Set the actual output over voltage protection value."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OVP {value}\r".encode())

        @property
        def ocpEnable(self) -> bool:
            """Get the actual output over current protection state."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OCP:STAT?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"ON"

        @ocpEnable.setter
        def ocpEnable(self, value: bool):
            """Enable or disable the actual output over current protection state."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OCP:STAT {"1" if value else "0"}\r".encode())

        @property
        def ocpValue(self) -> float:
            """Get the actual output over current protection value."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OCP?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip())

        @ocpValue.setter
        def ocpValue(self, value: float):
            """Set the actual output over current protection value."""
            self._gwinstekgpp._serial.write(f":OUTP{self._channel}:OCP {value}\r".encode())

        def setSource(self, sourceType: "Gwinstekgpp.SourceType", value: float):
            """Set the actual voltage or current target"""
            self._gwinstekgpp._serial.write(f":SOUR{self._channel}:{sourceType.toSerialStr()} {value}\r".encode())

        def getSource(self, sourceType: "Gwinstekgpp.SourceType") -> float:
            """Get the actual voltage or current target"""
            self._gwinstekgpp._serial.write(f":SOUR{self._channel}:{sourceType.toSerialStr()}?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip())

        @property
        def currentLimitState(self) -> bool:
            """Return true if the current limit has been reached"""
            self._gwinstekgpp._serial.write(f":SOUR{self._channel}:CURR:STAT?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"1"

        @property
        def voltageSet(self) -> float:
            """Return the actual voltage target (vset)."""
            self._gwinstekgpp._serial.write(f"VSET{self._channel}?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip().removesuffix(b"V"))

        @voltageSet.setter
        def voltageSet(self, value: float):
            """Set the actual voltage target (vset)."""
            self._gwinstekgpp._serial.write(f"VSET{self._channel}:{value}\r".encode())

        @property
        def currentSet(self) -> float:
            """Return the actual current target (iset)."""
            self._gwinstekgpp._serial.write(f"ISET{self._channel}?\r".encode())
            return float(self._gwinstekgpp._serial.readline().strip().removesuffix(b"V"))

        @currentSet.setter
        def currentSet(self, value: float):
            """Set the actual current target (iset)."""
            self._gwinstekgpp._serial.write(f"ISET{self._channel}:{value}\r".encode())

        @property
        def ch1Ch2Mode(self) -> "Gwinstekgpp.Ch1Ch2Mode":
            """Return the actual CH1/CH2 mode"""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"CH1/CH2 mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f"MODE{self._channel}?\r".encode())
            return Gwinstekgpp.Ch1Ch2Mode.fromSerialStr(self._gwinstekgpp._serial.readline().strip().decode())

        @property
        def loadCvEnable(self) -> bool:
            """Get the actual load mode in constant voltage mode."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:CV?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"ON"

        @loadCvEnable.setter
        def loadCvEnable(self, value: bool):
            """Enable or disable the actual load mode in constant voltage mode."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:CV {"ON" if value else "OFF"}\r".encode())

        @property
        def loadCcEnable(self) -> bool:
            """Get the actual load mode in constant current mode."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:CC?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"ON"

        @loadCcEnable.setter
        def loadCcEnable(self, value: bool):
            """Enable or disable the actual load mode in constant current mode."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:CC {"ON" if value else "OFF"}\r".encode())

        @property
        def loadCrEnable(self) -> bool:
            """Get the actual load mode in constant resistance mode."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:CR?\r".encode())
            return self._gwinstekgpp._serial.readline().strip() == b"ON"

        @loadCrEnable.setter
        def loadCrEnable(self, value: bool):
            """Enable or disable the actual load mode in constant resistance mode."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:CR {"ON" if value else "OFF"}\r".encode())

        @property
        def resistanceSet(self) -> int:
            """Return the actual resistance target (Rset)."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:RES?\r".encode())
            return int(self._gwinstekgpp._serial.readline().strip())

        @resistanceSet.setter
        def resistanceSet(self, value: int):
            """Set the actual resistance target (Rset)."""
            if self._channel != 1 and self._channel != 2:
                raise ValueError(f"Load mode not available for channel {self._channel}")
            self._gwinstekgpp._serial.write(f":LOAD{self._channel}:RES {value}\r".encode())

    def __init__(self, port: str):
        """Create a serial connection with a GW instek GPP power supply.
        
        @param port: The serial port to use, for exemple on Linux /dev/ttyUSB0
        """
        self._serial = serial.Serial(port=port, baudrate=9600, bytesize=8, parity=serial.PARITY_NONE, stopbits=1)
        self._serial.write(b"*IDN?\r")
        response = self._serial.readline()
        self._productBrand, self._productModel, self._productSerial, self._firmwareVersion = response.strip().split(b',')
        self._channels: dict[int, Gwinstekgpp.Channel] = dict()
        for channel in range(1, 5):
            self._channels[channel] = Gwinstekgpp.Channel(self, channel)

    @property
    def productBrand(self) -> str:
        """The product brand, for exemple "GW Instek" """
        return self._productBrand.decode()
    
    @property
    def productModel(self) -> str:
        """The product model, for exemple "GPP-4323" """
        return self._productModel.decode()

    @property
    def productSerial(self) -> str:
        """The product serial, for exemple "SN:AAA000000" """
        return self._productSerial.decode()

    @property
    def firmwareVersion(self) -> str:
        """The firmware version, for exemple "V1.22" """
        return self._firmwareVersion.decode()

    @staticmethod
    def _channelCheck(channel: int):
        if type(channel) != int:
            raise TypeError(f"Invalid channel type {type(channel)}")
        if channel<1 or 4<channel:
            raise ValueError(f"Invalid channel value {channel}")

    def channel(self, channel:int) -> Channel:
        Gwinstekgpp._channelCheck(channel)
        return self._channels[channel]

    def measureAll(self, measureType: MeasureType) -> list[float]:
        """Return the given measure for the all channel"""
        if measureType == Gwinstekgpp.MeasureType.ALL:
            raise ValueError("Get all measure is not supported for all channel")
        self._serial.write(f":MEAS:{measureType.toSerialStr()}:ALL?\r".encode())
        return [float(x) for x in self._serial.readline().strip().split(b',')]

    def setOutputStateAll(self, value: bool):
        """Set the actual output state of all channels."""
        # Same effect as next line self._serial.write(f":ALLOUT{"ON" if value else "OFF"}\r".encode())
        self._serial.write(f"OUT{"1" if value else "0"}\r".encode())

    def sourceAll(self, sourceType: SourceType) -> list[float]:
        """Return the actual current or voltage limit for the all channel"""
        if sourceType == Gwinstekgpp.SourceType.RESISTOR:
            raise ValueError("Get actual resistor limit is not supported for all channel")
        self._serial.write(f":SOUR:{sourceType.toSerialStr()}:ALL?\r".encode())
        return [float(x) for x in self._serial.readline().strip().split(b',')]

    class Ch1Ch2TrackingMode(enum.Enum):
        INDEPENDANT = 0
        SERIES = 1
        PARALLEL = 2

        def toSerialStr(self):
            return self.name[0:3]

    def setCh1Ch2TrackingMode(self, mode: Ch1Ch2TrackingMode, enable: bool):
        """Enable or Disable the given CH1/CH2 tracking mode"""
        if mode == Gwinstekgpp.Ch1Ch2TrackingMode.INDEPENDANT:
            raise ValueError(f"Cannot enable or disable {mode.name} mode")
        self._serial.write(f"OUTP:{mode.toSerialStr()} {"ON" if enable else "OFF"}\r".encode())

    def setCh1Ch2TrackingMode(self, mode: Ch1Ch2TrackingMode):
        """Set CH1/CH2 in the given tracking mode"""
        self._serial.write(f"TRACK{mode.value}\r".encode())

    class DisplayBrightness(enum.Enum):
        LOW = 1
        MIDDLE = 2
        HIGH = 3

    @property
    def displayBrightness(self) -> DisplayBrightness:
        """Get the current backlight display level."""
        self._serial.write(f":DISP:BRIG?\r".encode())
        return Gwinstekgpp.DisplayBrightness[self._serial.readline().strip().decode().upper()]

    @displayBrightness.setter
    def displayBrightness(self, value: DisplayBrightness):
        """Set the backlight display level."""
        self._serial.write(f":DISP:BRIG {value.name}\r".encode())

    @property
    def displayType(self) -> int:
        """Get the current display type between 1 and 7."""
        self._serial.write(f":DISP:TYPE?\r".encode())
        return int(self._serial.readline().strip())

    @staticmethod
    def _displayTypeCheck(displayType: int):
        if type(displayType) != int:
            raise TypeError(f"Invalid display type type {type(displayType)}")
        if channel<1 or 7<channel:
            raise ValueError(f"Invalid display type value {displayType}")

    @displayType.setter
    def displayType(self, value: int):
        """Set the current display type between 1 and 7."""
        Gwinstekgpp._displayTypeCheck(value)
        self._serial.write(f":DISP:TYPE {value}\r".encode())

    def err(self) -> str:
        self._serial.write(f":SYST:ERR?\r".encode())
        return self._serial.readline().strip().decode()


if __name__ == "__main__":
    gwinstekgpp = Gwinstekgpp("/dev/ttyUSB0")
    print(f"info: {gwinstekgpp.productBrand} {gwinstekgpp.productModel} {gwinstekgpp.productSerial} {gwinstekgpp.firmwareVersion}")
    for channelNum in range(1, 5):
        channel = gwinstekgpp.channel(channelNum)
        print(f"{channelNum}: "
              f"voltage={channel.measure(Gwinstekgpp.MeasureType.VOLTAGE)}V "
              f"current={channel.measure(Gwinstekgpp.MeasureType.CURRENT)}A "
              f"power={channel.measure(Gwinstekgpp.MeasureType.POWER)}W "
              f"all={channel.measure(Gwinstekgpp.MeasureType.ALL)} "
              f"voltage={channel.voltage}V current={channel.current}A "
              f"state={channel.outputEnable} "
              f"ovpState={channel.ovpEnable} ovpValue={channel.ovpValue} "
              f"ocpState={channel.ocpEnable} ocpValue={channel.ocpValue} "
              f"voltageSet={channel.voltageSet} currentSet={channel.currentSet} "
              )
        if channelNum == 1 or channelNum == 2:
            print(f"{channelNum}: CH1/CH2 mode={channel.ch1Ch2Mode.name}")
        if False:
            # Test output state
            state = gwinstekgpp.getOutputState(channel)
            gwinstekgpp.setOutputState(channel, not state)
            time.sleep(1)
            gwinstekgpp.setOutputState(channel, state)
            time.sleep(1)
    print(f"voltage: {gwinstekgpp.measureAll(Gwinstekgpp.MeasureType.VOLTAGE)}")
    print(f"current: {gwinstekgpp.measureAll(Gwinstekgpp.MeasureType.CURRENT)}")
    print(f"power: {gwinstekgpp.measureAll(Gwinstekgpp.MeasureType.POWER)}")
    if False:
        # Test display brightness
        displayBrightnessSav = gwinstekgpp.displayBrightness
        for level in Gwinstekgpp.DisplayBrightness:
            print(f"displayBrightness: {level.name}")
            gwinstekgpp.displayBrightness = level
            time.sleep(1)
        print(f"displayBrightness: Restaure")
        gwinstekgpp.displayBrightness = displayBrightnessSav
    if False:
        # Test display type
        displayTypeSav = gwinstekgpp.displayType
        for displayType in range(1, 8):
            print(f"displayType: {displayType}")
            gwinstekgpp.displayType = displayType
            time.sleep(1)
        print(f"displayType: Restaure")
        gwinstekgpp.displayType = displayTypeSav
    if False:
        # Test output state all
        print("Set output state all on")
        gwinstekgpp.setOutputStateAll(True)
        time.sleep(1)
        print("Set output state all off")
        gwinstekgpp.setOutputStateAll(False)
        time.sleep(1)
    if False:
        # Test CH1/CH2 tracking mode
        print("Enable CH1/CH2 in tracking series mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.SERIES, True)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_SERIES
        print("Disable CH1/CH2 in tracking series mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.SERIES, False)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_INDEPENDENT
        print("Enable CH1/CH2 in tracking parallel mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.PARALLEL, True)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_PARALLEL
        print("Disable CH1/CH2 in tracking parallel mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.PARALLEL, False)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_INDEPENDENT
    if False:
        # Test CH1/CH2 tracking mode
        print("Set CH1/CH2 in tracking series mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.SERIES)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_SERIES
        print("Set CH1/CH2 in tracking parallel mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.PARALLEL)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_PARALLEL
        print("Set CH1/CH2 in tracking independant mode")
        gwinstekgpp.setCh1Ch2TrackingMode(Gwinstekgpp.Ch1Ch2TrackingMode.INDEPENDANT)
        time.sleep(5)
        assert gwinstekgpp.channel(1).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.POWER_INDEPENDENT
    if True:
        # Test CH1/CH2 load mode
        print("Enable CH1 in load voltage mode")
        gwinstekgpp.channel(1).loadCvEnable = True
        time.sleep(5)
        assert gwinstekgpp.channel(1).loadCvEnable
        print("Disable CH1 in load voltage mode")
        gwinstekgpp.channel(1).loadCvEnable = False
        time.sleep(5)
        assert not gwinstekgpp.channel(1).loadCvEnable
        print("Enable CH1 in load current mode")
        gwinstekgpp.channel(1).loadCcEnable = True
        time.sleep(5)
        assert gwinstekgpp.channel(1).loadCcEnable
        print("Disable CH1 in load current mode")
        gwinstekgpp.channel(1).loadCcEnable = False
        time.sleep(5)
        assert not gwinstekgpp.channel(1).loadCcEnable
        print("Enable CH1 in load resistance mode")
        gwinstekgpp.channel(1).loadCrEnable = True
        time.sleep(5)
        assert gwinstekgpp.channel(1).loadCrEnable
        print("Disable CH1 in load resistance mode")
        gwinstekgpp.channel(1).loadCrEnable = False
        time.sleep(5)
        assert not gwinstekgpp.channel(1).loadCrEnable

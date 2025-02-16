#!/usr/bin/python3

from gwinstekgpp import Gwinstekgpp
import time
import sys


# Input
inputVoltageSetNominal = 8.0 # V
inputVoltageSetMin = 6.000 # V
inputVoltageSetMax = 8.400 # V
inputVoltageSetStep = 0.050 # V
inputVoltageSetChannelNum = 4
inputVoltageMeasureChannelNum = 1
# Output
outputCurrentSetNominal = 0.4 # A
outputCurrentSetMin = 0.000 # A
outputCurrentSetMax = 1.000 # A
outputCurrentSetStep = 0.025 # A
outputCurrentSetChannelNum = 2
outputVoltageMeasureChannelNum = 3

gwinstekgpp = Gwinstekgpp("/dev/ttyUSB0")


print("WARNING this script assume:")
print(f"- Channel {inputVoltageSetChannelNum} is in power mode and use as voltage input between "
      f"{inputVoltageSetMin}V and {inputVoltageSetMax}V of the device under test and to measure "
      "current")
assert gwinstekgpp.channel(inputVoltageSetChannelNum).outputEnable
assert gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet == 0.0 \
    or (inputVoltageSetMin <= gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet \
        and gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet <= inputVoltageSetMax)

print(f"- Channel {outputCurrentSetChannelNum} is in load mode with Iset between "
      f"{outputCurrentSetMin}A and {outputCurrentSetMax}A and only use to measure output voltage")
assert gwinstekgpp.channel(outputCurrentSetChannelNum).outputEnable
assert gwinstekgpp.channel(outputCurrentSetChannelNum).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.LOAD_CC
assert gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet == 0.0 \
    or (outputCurrentSetMin <= gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet \
        and gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet <= outputCurrentSetMax)

for channel in [inputVoltageMeasureChannelNum, outputVoltageMeasureChannelNum]:
    if channel in [1, 2]:
        print(f"- Channel {channel} is in load mode with Iset=0.0A and only use to "
            "measure input voltage")
        assert gwinstekgpp.channel(channel).ch1Ch2Mode == Gwinstekgpp.Ch1Ch2Mode.LOAD_CC
    else:
        print(f"- Channel {channel} is in power mode with Vset=0.0V and "
            "Iset=0.0A and only use to measure output voltage")
        assert gwinstekgpp.channel(channel).voltageSet == 0.0
    assert gwinstekgpp.channel(channel).outputEnable
    assert gwinstekgpp.channel(channel).currentSet == 0.0

input("Press Enter to continue...")


def printMeasure():
    inputVoltageSet = gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet
    outputCurrentSet = gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet
    inputVoltage = gwinstekgpp.channel(inputVoltageMeasureChannelNum).voltage
    inputCurrent = gwinstekgpp.channel(inputVoltageSetChannelNum).current
    ouputVoltage = gwinstekgpp.channel(outputVoltageMeasureChannelNum).voltage
    outputCurrent = gwinstekgpp.channel(outputCurrentSetChannelNum).current
    inputPower = inputVoltage * inputCurrent
    outputPower = ouputVoltage * outputCurrent
    if inputPower != 0.0:
        efficiency = outputPower / inputPower * 100.0
    else:
        efficiency = 0.0
    print(f"{inputVoltageSet}, {outputCurrentSet}, {inputVoltage}, {inputCurrent}, {ouputVoltage}, {outputCurrent}, "
          f"{inputPower}, {outputPower}, {efficiency}")


print("")
gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet = inputVoltageSetNominal
time.sleep(1)
gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet = outputCurrentSetNominal
inputVoltageSet = inputVoltageSetMin
print("inputVoltageSet, outputCurrentSet, inputVoltage, inputCurrent, ouputVoltage, outputCurrent, inputPower, "
      "outputPower, efficiency")
while True:
    gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet = inputVoltageSet
    time.sleep(1)
    printMeasure()
    if gwinstekgpp.channel(inputVoltageSetChannelNum).currentLimitState:
        print("ERROR current limit raise in channel input voltage")
        break
    inputVoltageSet += inputVoltageSetStep
    if inputVoltageSet > inputVoltageSetMax:
        break
gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet = 0.0
time.sleep(1)
gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet = 0.0
time.sleep(1)


print("")
gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet = inputVoltageSetNominal
time.sleep(1)
gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet = outputCurrentSetNominal
outputCurrentSet = outputCurrentSetMin
print("inputVoltageSet, outputCurrentSet, inputVoltage, inputCurrent, ouputVoltage, outputCurrent, inputPower, "
      "outputPower, efficiency")
while True:
    gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet = outputCurrentSet
    time.sleep(1)
    printMeasure()
    if gwinstekgpp.channel(inputVoltageSetChannelNum).currentLimitState:
        print("ERROR current limit raise in channel input voltage")
        break
    outputCurrentSet += outputCurrentSetStep
    if outputCurrentSet > outputCurrentSetMax:
        break
gwinstekgpp.channel(outputCurrentSetChannelNum).currentSet = 0.0
time.sleep(1)
gwinstekgpp.channel(inputVoltageSetChannelNum).voltageSet = 0.0
time.sleep(1)

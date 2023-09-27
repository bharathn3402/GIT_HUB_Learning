from intelhex import IntelHex
import os.path
import math
from os import listdir

# Import serial library for communication with Arduino
import serial
import serial.tools.list_ports
import time
from datetime import datetime

def selectHexFile():
    presentFiles = [file for file in os.listdir() if os.path.isfile(file)]
    hexFiles = [file for file in presentFiles if file.endswith(".hex")]
    return hexFiles

def comPortSelection():
    """*****************   COM port selection   ************************"""
    list_portsAvailable = list(serial.tools.list_ports.comports())
    return list_portsAvailable

def setupSerialComm(COMport, baudRate, timeOut):
    """Setup serial communication"""
    try:
        targetArduino = serial.Serial(COMport, baudRate, timeout=timeOut, write_timeout=timeOut, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        return targetArduino
    except Exception as error:
        raise SerialConnectionError(f"Error while setting up serial communication: {str(error)}")
    
    
def sendArduinoCANframe(targetArduino = [], listOfBytes = [], byteFrame1 = [], byteFrame2 = []):
    writtenBytes = 0
    if listOfBytes != []:
        for byteIndex in range(len(listOfBytes)):
            writtenBytes = writtenBytes + targetArduino.write(listOfBytes[byteIndex].to_bytes(1, byteorder='big'))
    if byteFrame1 != []:
        for byte in byteFrame1:
            writtenBytes = writtenBytes + targetArduino.write(byte.to_bytes(1, byteorder='big'))
    if byteFrame2 != []:
        for byte in byteFrame2:
            writtenBytes = writtenBytes + targetArduino.write(byte.to_bytes(1, byteorder='big'))

    time.sleep(0.01)
    return writtenBytes

class SerialConnectionError(Exception):
    pass

def Arduinohandshake(targetArduino):
    arduinoHandshakeFlag = 0
    arduinoHandshakeList = [0x0B, 0xA0]
    message = ""
    while True:  # Arduino handshake loop
        time.sleep(3)
        startTimeForArduinoHandshake = time.time()

        while (time.time() - startTimeForArduinoHandshake) < 30:
            try:
                targetArduino.write(arduinoHandshakeList[0].to_bytes(1, byteorder='big'))
            except Exception as error:
                break
            arduinoResponse = targetArduino.read(size=1)

            if arduinoResponse == b'\xB0':
                targetArduino.write(arduinoHandshakeList[1].to_bytes(1, byteorder='big'))
                arduinoResponse = targetArduino.read(size=1)

                if arduinoResponse == b'\x0A':
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    message = f"[{timestamp}]: Arduino handshake successful! "
                    arduinoHandshakeFlag = 1
                    break

        if arduinoHandshakeFlag == 1:
            return True, message
        else:
            targetArduino.close()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"{timestamp}: Arduino handshake unsuccessful! "
            return False, message
        
def mew_detect(startTimeForVCUhandshake,targetArduino):
    while (1):
        try:
            if ((time.time() - startTimeForVCUhandshake) < 60): #Check for VCU availability for 60 seconds
                arduinoResponse =targetArduino.read(size=10)
                if arduinoResponse != b'':
                    if arduinoResponse[0] == 0x51 and arduinoResponse[1] == 0x08:
                        msg="Mew bootloader detected!"
                        return 1,msg
                        break
            else:
                msg="Mew bootloader detection timeout!"
                return 0,msg
        except Exception as error:
            raise SerialConnectionError ("Arduino connection problem. Please restart utility.")


def mew_Handshake(selectedHexFile,targetArduino):
    HexFileName = selectedHexFile
    HexFileData = IntelHex()
    HexFileData.fromfile(HexFileName,format='hex')
    HexPyDictionary = HexFileData.todict()
    programMemoryStartAddress = HexFileData.minaddr()
    totalSize = HexFileData.maxaddr() - HexFileData.minaddr() +1
    programExecutionStartAddress = HexFileData.start_addr['EIP']
    segmentList = HexFileData.segments()
    numberOfDataSegments = len(segmentList)
    communicationOkayFlag = 0 

    try:
        startAddressBytes = programMemoryStartAddress.to_bytes(4, byteorder='big', signed=False)
        vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
        writtenBytes = sendArduinoCANframe(targetArduino, vcuInitList, startAddressBytes)

        executionStartAddressBytes = programExecutionStartAddress.to_bytes(4, byteorder='big', signed=False)
        vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
        writtenBytes =sendArduinoCANframe(targetArduino, vcuInitList, executionStartAddressBytes)

        numberOfDataSegmentsBytes = numberOfDataSegments.to_bytes(2, byteorder='big', signed=False)
        totalSizeBytes = totalSize.to_bytes(4, byteorder='big', signed=False)
        vcuInitList = [0x50, 0x08, 0xB0, 0x00]
        writtenBytes = sendArduinoCANframe(targetArduino, vcuInitList, numberOfDataSegmentsBytes, totalSizeBytes)
        arduinoResponse = targetArduino.read(size=10)
        if arduinoResponse != b'':   
            if arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x01:
                communicationOkayFlag = 1
                return communicationOkayFlag,numberOfDataSegments
            elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:
                communicationOkayFlag=0
                return communicationOkayFlag
        else:
            communicationOkayFlag=None
            return communicationOkayFlag

        # return arduinoResponse,numberOfDataSegments
    except Exception as error:
        raise SerialConnectionError(error)




def flashFirmware(numberOfSegments,segment,HexPyDictionary, targetArduino,firmwareFlashedSuccessfully ):
    try:
        numberOfSegments = numberOfSegments+1
        segmentStartAddress = segment[0]
        segmentEndAddress = segment[1] - 1
        segementMemory = segmentEndAddress - segmentStartAddress + 1

        CANdataBytes = [0x50, 0x08, 0xB0, 0x01, 0x00, 0x00]
        segmentStartAddressBytes = segmentStartAddress.to_bytes(4, byteorder='big', signed=False)
        writtenBytes = sendArduinoCANframe(targetArduino, CANdataBytes, segmentStartAddressBytes)

        pageByteCount = 0 #Reset when reaches 128
        fourByteCount = 0
        dataByteList = []
        for byteAddres in range(segmentStartAddress, segmentEndAddress+1):
            dataByteList = dataByteList + [HexPyDictionary[byteAddres]]
            fourByteCount = fourByteCount+1
            
            if fourByteCount == 4 or byteAddres == segmentEndAddress:
                if byteAddres == segmentEndAddress:
                    CANdataBytes = [0x50, 0x08, 0xB0, 0x03, 0x00, 0x00] + dataByteList
                    if fourByteCount < 4:
                        CANdataBytes = CANdataBytes + [0xFF] * (4 - fourByteCount)

                else:
                    CANdataBytes = [0x50, 0x08, 0xB0, 0x02, 0x00, 0x00] + dataByteList
                
                pageByteCount = pageByteCount+4
                fourByteCount = 0
                dataByteList = []

                targetArduino.flushInput()
                writtenBytes = sendArduinoCANframe(targetArduino, CANdataBytes)
                
            if (pageByteCount == 128) or byteAddres == segmentEndAddress:
                arduinoResponse = targetArduino.read(size=10)
                if arduinoResponse == b'':
                    message="\nVCU comm. timeout!\n"
                    firmwareFlashedSuccessfully = False
                    return firmwareFlashedSuccessfully,message,numberOfSegments
                if arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:
                    message="\nVCU comm. error!\n"
                    firmwareFlashedSuccessfully = False
                    return firmwareFlashedSuccessfully,message,numberOfSegments
                elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x04:
                    pageByteCount = 0
                    continue
    except Exception as error:
        firmwareFlashedSuccessfully = False
        msg=str(error)+" communication problem"
        raise SerialConnectionError (msg)

    if firmwareFlashedSuccessfully:
        message=(str(numberOfSegments) + ": Segment written successfully.\n")
        return firmwareFlashedSuccessfully,message,numberOfSegments
        
    else:
        return None



def calculateChecksum(segment):
    segmentStartAddress = segment[0]
    segmentEndAddress = segment[1] - 1
    segmentMemory = segmentEndAddress - segmentStartAddress + 1

    segmentCheckSum = 0
    for byteAddress in range(segmentStartAddress, segmentEndAddress + 1, 4):
        tempSum = 0
        if (segmentEndAddress - byteAddress) >= 3:
            tempSum = (
                (HexPyDictionary[byteAddress] << 24)
                | (HexPyDictionary[byteAddress + 1] << 16)
                | (HexPyDictionary[byteAddress + 2] << 8)
                | (HexPyDictionary[byteAddress + 3])
            )
        else:
            shiftBits = 24
            for index in range(byteAddress, segmentEndAddress + 1):
                tempSum = tempSum | (HexPyDictionary[index] << (shiftBits))
                shiftBits = shiftBits - 8

            for index in range(0, 3 - (segmentEndAddress - byteAddress)):
                tempSum = tempSum | (0xFF << (shiftBits))
                shiftBits = shiftBits - 8

        if (segmentCheckSum + tempSum) > 0xFFFFFFFF:
            segmentCheckSum = tempSum - (1 + 0xFFFFFFFF - segmentCheckSum)
        else:
            segmentCheckSum = segmentCheckSum + tempSum

    return segmentCheckSum

def validateChecksum(targetArduino, segmentList, segmentIndex):
    segment = segmentList[segmentIndex]
    segmentStartAddress = segment[0]
    segmentMemory = segment[1] - segment[0]

    segmentCheckSum = calculateChecksum(segment)

    CANdataBytes = [0x50, 0x08, 0xB0, 0x00]
    CANdataBytes += [0x01 | ((segmentIndex + 1) << 4)] + [0x00]
    segmentStartAddressBytes = segmentStartAddress.to_bytes(
        4, byteorder="big", signed=False
    )
    writtenBytes = sendArduinoCANframe(targetArduino, CANdataBytes, segmentStartAddressBytes)

    CANdataBytes = [0x50, 0x08, 0xB0, 0x00]
    CANdataBytes += [0x02 | ((segmentIndex + 1) << 4)] + [0x00]
    segmentMemoryBytes = segmentMemory.to_bytes(4, byteorder="big", signed=False)
    writtenBytes = sendArduinoCANframe(targetArduino, CANdataBytes, segmentMemoryBytes)

    CANdataBytes = [0x50, 0x08, 0xB0, 0x00]
    CANdataBytes += [0x03 | ((segmentIndex + 1) << 4)] + [0x00]
    segmentChecksumBytes = segmentCheckSum.to_bytes(4, byteorder="big", signed=False)
    writtenBytes = sendArduinoCANframe(
        targetArduino, CANdataBytes, segmentChecksumBytes
    )

    arduinoResponse = targetArduino.read(size=10)

    if arduinoResponse == b"":
        print("\nVCU comm. timeout!\n")
        return False

    if (
        arduinoResponse[0] == 0x51
        and arduinoResponse[3] == 0x02
        and arduinoResponse[4] == (0x04 | ((segmentIndex + 1) << 4))
    ):
        print(
            "\nMemory segment checksum mismatch! VCU Segment checksum: "
            + hex(vcuSegmentChecksum)
            + ".\n\nProceeding to flash.\n"
        )
        CANdataBytes = [0x50, 0x08, 0xB0, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x00]
        writtenBytes = sendArduinoCANframe(targetArduino, CANdataBytes)
        return False

    if (
        arduinoResponse[0] == 0x51
        and arduinoResponse[3] == 0x01
        and arduinoResponse[4] == (0x04 | ((segmentIndex + 1) << 4))
    ):
        print("Memory segment checksum identical.\n")
        return True

    return False

# for index, segment in enumerate(reversed(segmentList)):
#     try:
#         if validateChecksum(targetArduino, segmentList, index):
#             print(str(index + 1) + ": Segment written successfully.\n")
#         else:
#             break
#     except Exception as error:
#         firmwareFlashedSuccessfully = False
#         communicationOkayFlag = 0

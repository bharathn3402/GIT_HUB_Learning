from intelhex import IntelHex
import os.path
import math
from os import listdir

# Import serial library for communication with Arduino
import serial
import serial.tools.list_ports

import time

arduinoTimeOut = 10     # Value in seconds, None for infinite wait

def selectHexFile():
    while 1:
        presentFiles = [file for file in os.listdir() if os.path.isfile(file)]
        HexFiles = [file for file in presentFiles if ".hex" in file]
        print("\n")
        if len(HexFiles) > 0:
            for index, file in enumerate(HexFiles):
                print(str(index+1) + ": " + file)
            break
        else:
            input("Kindly keep the HEX files in current directory and then enter 'R': ")

    userFileInputMessage = "\nPlease enter the index of the HEX file: "
    while 1:
        try:
            HexFileIndex = int(input(userFileInputMessage))-1
            
            if HexFileIndex >= len(HexFiles) or HexFileIndex < 0:
                raise Exception("Index out of bound!")
            
            HexFileName = HexFiles[HexFileIndex]
            if os.path.exists(HexFileName):
                return HexFileName
                break
            else:
                print("No file exists in the current directory with the input name.\nProvide the correct name.\n")
        except Exception as msg:
            print("Error!\n" + str(msg))
            continue


def comPortSelection():
    while 1:
        """*****************   COM port selection   ************************"""
        # Find & print available COM ports
        print("\nAvailble COM ports:")
        list_portsAvailable = list(serial.tools.list_ports.comports())
        for count, port in enumerate(list_portsAvailable, 1):
            print(str(count) + ": " + str(port))

        # Ask user for Arduino COM port number
        while 1:
            try:
                COMport_index = int(input("Enter the index of Arduino COMport: "))
                if COMport_index < 1 or COMport_index > len(list_portsAvailable):
                    raise Exception("Entered index out of bound!")
                else:
                    break
            except Exception as error:
                print("Oops! Seems like you entered an invalid index!")

        return list_portsAvailable[COMport_index-1].device
        """************      COM port selection ends          **************"""


def setupSerialComm(COMport=[],baudRate=[], timeOut=[]):
    """******  Setup serial communication  ********"""
    while 1:
        try:
            targetArduino = serial.Serial(COMport, baudRate, timeout=timeOut, write_timeout=timeOut, bytesize=serial.EIGHTBITS, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE)
        except Exception as error:
            print(str(error))
            print("\nOops! Trouble initiating communication with Arduino.\n"
                  "Make sure Arduino is connected to the same COM-port that you mentioned.")
            while 1:
                try:
                    choice = int(input("\nDo you want to \n1> try again or 2> start over? "))
                    break
                except Exception as error:
                    print("Oops! Invalid choice.")
            if choice >= 2:
                return
            else:
                continue

        return targetArduino
    """******  Setup serial communication ends  ********"""

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


"""
Application Starts here
"""
print("\n\nWelcome to Mew utility.\n")
while 1:
    HexFileName = selectHexFile()
    #hexFileRawData = open(HexFileName, 'r')
    HexFileData = IntelHex()
    HexFileData.fromfile(HexFileName,format='hex')
    HexPyDictionary = HexFileData.todict()
    programMemoryStartAddress = HexFileData.minaddr()
    totalSize = HexFileData.maxaddr() - HexFileData.minaddr() +1
    programExecutionStartAddress = HexFileData.start_addr['EIP']
    segmentList = HexFileData.segments()
    numberOfDataSegments = len(segmentList)


    arduinoHandshakeFlag = 0
    arduinoHandshakeList = [0x0B, 0xA0]

    while 1: #Arduino handshake loop
        COMport = comPortSelection()
        targetArduino = setupSerialComm(COMport=COMport, baudRate=115200, timeOut=arduinoTimeOut)
        time.sleep(3)
        #targetArduino.flushInput()
        #targetArduino.flushOutput()
        startTimeForArduinoHandshake = time.time()
        while ((time.time() - startTimeForArduinoHandshake) < 30):
            try:
                targetArduino.write(arduinoHandshakeList[0].to_bytes(1, byteorder='big'))
            except Exception as error:
                break
            arduinoResponse = targetArduino.read(size=1)
            if arduinoResponse == b'\xB0':
                targetArduino.write(arduinoHandshakeList[1].to_bytes(1, byteorder='big'))
                arduinoResponse = targetArduino.read(size=1)
                if arduinoResponse == b'\x0A':
                    print("\nArduino Handshake successful!\n")
                    arduinoHandshakeFlag = 1
                    break

        
        if arduinoHandshakeFlag == 1:
            break
        else:
            targetArduino.close()
            print("\nArduino Handshake unsuccessful!\n")
            userChoice = int(input("Do you want to \n1> Try again or 2> Exit? "))
            if userChoice == 1:
                continue
            else:
                exit()


    communicationOkayFlag = 0

    if arduinoHandshakeFlag == 1:
        targetArduino.flushInput()

        startTimeForVCUhandshake = time.time()
        
        while (1):
            try:
                if ((time.time() - startTimeForVCUhandshake) < 60): #Check for VCU availability for 60 seconds
                    arduinoResponse = targetArduino.read(size=10)
                    if arduinoResponse != b'':
                        if arduinoResponse[0] == 0x51 and arduinoResponse[1] == 0x08:
                            print("Mew bootloader detected!\n")
                            break
                else:
                    print("Mew bootloader detection timeout!\n")
                    userChoice = int(input("Do you want to \n1> Try again or 2> Exit? "))
                    if userChoice == 1:
                        print("\nPlease power cycle the Mew.\n")
                        startTimeForVCUhandshake = time.time()
                        continue
                    else:
                        exit()

            except Exception as error:
                print("Arduino connection problem. Please restart utility.")
                time.sleep(10)
                exit()

        try:
            startAddressBytes = programMemoryStartAddress.to_bytes(4, byteorder='big', signed=False)
            vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
            writtenBytes = sendArduinoCANframe(targetArduino, vcuInitList, startAddressBytes)

            executionStartAddressBytes = programExecutionStartAddress.to_bytes(4, byteorder='big', signed=False)
            vcuInitList = [0x50, 0x08, 0xB0, 0x00, 0x00, 0x00]
            writtenBytes = sendArduinoCANframe(targetArduino, vcuInitList, executionStartAddressBytes)

            numberOfDataSegmentsBytes = numberOfDataSegments.to_bytes(2, byteorder='big', signed=False)
            totalSizeBytes = totalSize.to_bytes(4, byteorder='big', signed=False)
            vcuInitList = [0x50, 0x08, 0xB0, 0x00]
            writtenBytes = sendArduinoCANframe(targetArduino, vcuInitList, numberOfDataSegmentsBytes, totalSizeBytes)

            arduinoResponse = targetArduino.read(size=10)

            if arduinoResponse != b'':
                if arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x01:
                    communicationOkayFlag = 1
                    print("\nMew handshake successful!  Uploading firmware.\nNumber of memory segments in hex file: " + str(numberOfDataSegments) + "\n\n")
                elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:
                    communicationOkayFlag = 0
            else:
                print("Mew handshake timeout! Please restart the utility.")
                time.sleep(10)
                exit()

        except Exception as error:
                print("Arduino connection problem. Please restart utility.")
                time.sleep(10)
                exit()


        if communicationOkayFlag != 1:
            print("Mew denied communication! Please restart the utility.")
            time.sleep(10)
            exit()

        numberOfSegments = 0
        firmwareFlashedSuccessfully = True
        for segment in reversed(segmentList):
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
                            print("\nVCU comm. timeout!\n")
                            firmwareFlashedSuccessfully = False
                            break
                        elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x10:
                            print("\nVCU comm. error!\n")
                            firmwareFlashedSuccessfully = False
                            break
                        elif arduinoResponse[0] == 0x51 and arduinoResponse[3] == 0x04:
                            pageByteCount = 0
                            continue
            
            except Exception as error:
                firmwareFlashedSuccessfully = False

            if firmwareFlashedSuccessfully:
                print(str(numberOfSegments) + ": Segment written successfully.\n")
                continue
            else:
                break

     
    #else:
    #    firmwareFlashedSuccessfully = False

    #targetArduino.close()

    if firmwareFlashedSuccessfully:
        print("\nFirmware flashed successfully!\n")
        userChoice = int(input("\nDo you want to \n1> Flash firmware again or 2> Exit? "))
        if userChoice == 1:
            targetArduino.close()
            continue
        else:
            exit()
    else:
        print("\nFirmware flashing unsuccessfull! Please restart the utility.\n")
        time.sleep(10)
        exit()

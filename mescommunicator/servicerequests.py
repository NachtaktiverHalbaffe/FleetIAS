"""
Filename: servicerequests.py
Version name: 1.0, 2021-07-21
Short description: servicerequests which can be send and received to mes

(C) 2003-2021 IAS, Universitaet Stuttgart

"""
import math


class ServiceRequests(object):

    def __init__(self):
        self.msg = ""
        # Parameter for service calls
        self.tcpIdent = "33333301"
        self.requestID = 0
        self.mClass = 0
        self.mNo = 0
        self.errorState = 0
        self.dataLength = 0
        self.resourceId = 0
        self.oNo = 0
        self.oPos = 0
        self.wpNo = 0
        self.opNo = 0
        self.bufNo = 0
        self.bufPos = 0
        self.carrierId = 0
        self.palletID = 0
        self.palletPos = 0
        self.pNo = 0
        self.stopperId = 0
        self.errorStepNo = 0
        self.stepNo = 0
        self.maxRecords = 0
        self.boxId = 0
        self.boxPos = 0
        self.mainOPos = 0
        self.beltNo = 0
        self.cNo = 0
        self.boxPNo = 0
        self.palletPNo = 0
        self.aux1Int = 0
        self.aux2Int = 0
        self.aux1DInt = 0
        self.aux2DInt = 0
        self.mainPNo = 0
        self.serviceParams = []

    # request to get transport tasks
    # @param:
    #   noOfActiveAGV: number of active robotinos which can execute tasks
    def getTransportTasks(self, noOfActiveAGV):
        # serviceclass and servicenumber to identify request
        self.mClass = 200
        self.mNo = 21
        # number of tasks returned by mes
        self.maxRecords = noOfActiveAGV

    # read the transport task from an response from the mes
    # @return:
    #   transportTasks: set of transport tasks, each item is a tupel with: (startId, targetId)
    def readTransportTasks(self):
        # check if data is a transport task
        if self.mClass == 200 and self.mNo == 21:
            transportTasks = set()
            for i in range(int(len(self.serviceParams)/8)):
                startId = self.serviceParams[8*i]
                targetId = self.serviceParams[8*i+4]
                task = (startId, targetId)
                # add task to transport task if startId and targetId are valid
                if startId != 0 and targetId != 0 and startId != targetId:
                    transportTasks.add(task)
            return transportTasks
        else:
            print("[SERVICEREQUESTS] Received data isnt a transport task")

    # inform mes about the current docking position
    # @params:
    #   dockedAt: resourceId of resource where it is docked at (undocked: dockedAt=0)
    #   robotinoID: resourceId of robotino which has docked
    def setDockingPos(self, dockedAt, robotinoID):
        # serviceclass and servicenumber to identify request
        self.mClass = 201
        self.mNo = 1
        # id of robotino
        self.aux1Int = int(robotinoID)
        # id of resource where robotino is docked
        self.resourceId = int(dockedAt)

    # inform mes that robotino loads/unloads carrier
    # @param:
    #   robotinoId: resourceId of the robotino which loads/unloads
    #   resourceId: resourceId of resource where it loads/unloads the carrier
    #   isLoading: if robotino loads (True) or unLoads(False) the carrier
    def moveBuf(self, robotinoId, resourceId, isLoading):
        # serviceclass and servicenumber to identify request
        self.mClass = 151
        self.mNo = 5
        self.dataLength = 12
        # set serviceparams depending on direction
        if isLoading:
            # serviceparams: [id of source, bufNo of source, bufPos of source,
            # id of target, bufNo of target, bufPos of target]
            self.serviceParams = [resourceId, 1, 1, robotinoId, 1, 1]
        else:
            self.serviceParams = [robotinoId, 1, 1, resourceId, 2, 1]

    # request mes to delete the buffer
    # @params:
    #   isBuffOut: if it is the Buffer Out (True) or Buffer In (False)
    #   robotinoId: resourceId of robotino which buffer should be deleted
    def delBuf(self,  robotinoId):
        # serviceclass and servicenumber to identify request
        self.mClass = 151
        self.mNo = 12
        # buffer number for buffer which should get deleted
        # 1= buffer out and 2= buffer in
        self.bufNo = 1
        # set resource id of resource
        self.resourceId = robotinoId

    # decodes message depending on the formatting specified by tcpident
    # @param:
    #   msg: tcp message
    def decodeMessage(self, msg):
        self.msg = msg
        if msg[:6] == '333333':
            self._decodeBin()
        elif '<CR>' in msg and len(msg.split("<CR>")) > 3:
            # msg is in shortened string format
            self._decodeStrShort()
        elif '=' in msg:
            # msg is in full string format
            self._decodeStrFull()
        else:
            print("[SERVICEREQUESTS] Error, couldn't decode message")

    # encodes message for PlcServiceOrderSocket in a format so it can be send
    def encodeMessage(self):
        self._printAttr()
        return self._encodeBin()

    # encodes message with full string format. Excluding the tcpident only the needed parameter are sent.
    # Format is parameter=value and each parameter is seperated with a ";"
    # @params: Takes all the neccessary attributes of the Object and parses them

    def _encodeStrFull(self):
        # Header
        msg = str(self.tcpIdent)
        if self.requestID != 0:
            msg += ";RequestId=" + str(self.requestID)
        if self.mClass != 0:
            msg += ";MClass=" + str(self.mClass)
        if self.mNo != 0:
            msg += ";MNo=" + str(self.mNo)
        if self.errorState != 0:
            msg += ";ErrorState=" + str(self.errorState)
        if self.dataLength != 0:
            msg += ";DataLength=" + str(self.dataLength)

        # standardparameter
        if self.resourceId != 0:
            msg += ";ResourceID=" + str(self.resourceId)
        if self.oNo != 0:
            msg += ";ONo=" + str(self.oNo)
        if self.oPos != 0:
            msg += ";OPos=" + str(self.oPos)
        if self.wpNo != 0:
            msg += ";WPNo=" + str(self.wpNo)
        if self.opNo != 0:
            msg += ";OpNo=" + str(self.opNo)
        if self.bufNo != 0:
            msg += ";BufNo=" + str(self.bufNo)
        if self.bufPos != 0:
            msg += ";BufPos=" + str(self.bufPos)
        if self.carrierId != 0:
            msg += ";CarrierID=" + str(self.carrierId)
        if self.palletID != 0:
            msg += ";PalletID=" + str(self.palletID)
        if self.palletPos != 0:
            msg += ";PalletPos=" + str(self.palletPos)
        if self.pNo != 0:
            msg += ";PNo=" + str(self.pNo)
        if self.stopperId != 0:
            msg += ";StopperID=" + str(self.stopperId)
        if self.errorStepNo != 0:
            msg += ";ErrorStepNo=" + str(self.errorStepNo)
        if self.stepNo != 0:
            msg += ";StepNo=" + str(self.stepNo)
        if self.maxRecords != 0:
            msg += ";MaxRecords=" + str(self.maxRecords)
        if self.boxId != 0:
            msg += ";BoxID=" + str(self.boxId)
        if self.boxPos != 0:
            msg += ";BoxPos=" + str(self.boxPNo)
        if self.mainOPos != 0:
            msg += ";MainOPos=" + str(self.mainOPos)
        if self.beltNo != 0:
            msg += ";BeltNo=" + str(self.beltNo)
        if self.cNo != 0:
            msg += ";CNo=" + str(self.cNo)
        if self.boxPNo != 0:
            msg += ";BoxPNo=" + str(self.boxPNo)
        if self.palletPNo != 0:
            msg += ";PalletPNo=" + str(self.palletPNo)
        if self.aux1Int != 0:
            msg += ";Aux1Int=" + str(self.aux1Int)
        if self.aux2Int != 0:
            msg += ";Aux2Int=" + str(self.aux2Int)
        if self.aux1DInt != 0:
            msg += ";Aux1DInt=" + str(self.aux1DInt)
        if self.aux2DInt != 0:
            msg += ";Aux2DInt=" + str(self.aux2DInt)
        if self.mainPNo != 0:
            msg += ";MainPNo=" + str(self.mainPNo)

        # service specific paramter. Each parameter is a 2 tuple with (parametername, parameter)
        for item in self.serviceParams:
            msg += ";" + item[0] + "=" + item[1]

        # evry message ends with <CR>
        msg += "<CR>"
        return msg

    def _decodeStrFull(self):
        # split parameter
        msg = self.msg.split(";")
        # saving all parameter into object
        for item in msg:
            # Header
            param = item.split("=")
            # replace <CR> if its in item
            if len(param) == 2:
                if "<CR>" in param[1]:
                    param[1] = param[1].replace('<CR>', '')
            if '444' in item or '445' in item:
                self.tcpIdent = int(item)
            elif 'RequestId' in item:
                self.requestID = param[1]
            elif 'MClass' in item:
                self.mClass = param[1]
            elif 'MNo' in item:
                self.mNo = param[1]
            elif 'ErrorState' in item:
                self.errorState = param[1]
            elif 'DataLength' in item:
                self.dataLength = param[1]

            # standardparameter
            elif 'ResourceID' in item:
                self.resourceId = param[1]
            elif 'ONo' in item:
                self.oNo = param[1]
            elif 'OPos' in item:
                self.oPos = param[1]
            elif 'wpNo' in item:
                self.wpNo = param[1]
            elif 'OpNo' in item:
                self.opNo = param[1]
            elif 'BufNo' in item:
                self.bufNo = param[1]
            elif 'BufPos' in item:
                self.bufPos = param[1]
            elif 'CarrierID' in item:
                self.carrierId = param[1]
            elif 'PalletID' in item:
                self.palletID = param[1]
            elif 'PalletPos' in item:
                self.palletPos = param[1]
            elif 'PNo' in item:
                self.pNo = param[1]
            elif 'StopperID' in item:
                self.stopperId = param[1]
            elif 'ErrorStepNo' in item:
                self.errorStepNo = param[1]
            elif 'StepNo' in item:
                self.stepNo = param[1]
            elif 'MaxRecords' in item:
                self.maxRecords = param[1]
            elif 'BoxID' in item:
                self.boxId = param[1]
            elif 'BoxPos' in item:
                self.boxPos = param[1]
            elif 'MainOPos' in item:
                self.mainOPos = param[1]
            elif 'BeltNo' in item:
                self.beltNo = param[1]
            elif 'CNo' in item:
                self.cNo = param[1]
            elif 'BoxPNo' in item:
                self.boxPNo = param[1]
            elif 'PalletPNo=' in item:
                self.palletPNo = param[1]
            elif 'Aux1Int' in item:
                self.aux1Int = param[1]
            elif 'Aux2Int' in item:
                self.aux2Int = param[1]
            elif 'Aux1DInt' in item:
                self.aux1DInt = param[1]
            elif 'Aux2DInt' in item:
                self.aux2DInt = param[1]
            elif 'MainPNo' in item:
                self.mainPNo = param[1]
            else:
                self.serviceParams.append((param[0], param[1]))

    # encodes message with shortemd string format. Like the binary format evry parameter is send in
    # the right order in ASCII and every parameter is seperated with a "<CR>"
    # @params: Takes all the neccessary attributes of the Object and parses them
    def _encodeStrShort(self):
        # header
        msg = "445<CR>"
        msg += str(self.requestID) + "<CR>"
        msg += str(self.mClass) + "<CR>"
        msg += str(self.mNo) + "<CR>"
        msg += str(self.errorState) + "<CR>"
        msg += str(self.dataLength) + "<CR>"

        # standard parameter
        msg += str(self.resourceId) + "<CR>"
        msg += str(self.oNo) + "<CR>"
        msg += str(self.oPos) + "<CR>"
        msg += str(self.wpNo) + "<CR>"
        msg += str(self.opNo) + "<CR>"
        msg += str(self.bufNo) + "<CR>"
        msg += str(self.bufPos) + "<CR>"
        msg += str(self.carrierId) + "<CR>"
        msg += str(self.palletID) + "<CR>"
        msg += str(self.palletPos) + "<CR>"
        msg += str(self.pNo) + "<CR>"
        msg += str(self.stopperId) + "<CR>"
        msg += str(self.errorStepNo) + "<CR>"
        msg += str(self.stepNo) + "<CR>"
        msg += str(self.maxRecords) + "<CR>"
        msg += str(self.boxId) + "<CR>"
        msg += str(self.boxPos) + "<CR>"
        msg += str(self.mainOPos) + "<CR>"
        msg += str(self.beltNo) + "<CR>"
        msg += str(self.cNo) + "<CR>"
        msg += str(self.boxPNo) + "<CR>"
        msg += str(self.palletPNo) + "<CR>"
        msg += str(self.aux1Int) + "<CR>"
        msg += str(self.aux2Int) + "<CR>"
        msg += str(self.aux1DInt) + "<CR>"
        msg += str(self.aux2DInt) + "<CR>"
        msg += str(self.mainPNo) + "<CR>"

        # service-specific parameter
        for item in self.serviceParams:
            msg += str(item) + "<CR>"
        return msg

    def _decodeStrShort(self):
        bytes = self.msg.split("<CR>")

        self.requestID = bytes[1]
        self.mClass = bytes[2]
        self.mNo = bytes[3]
        self.errorState = bytes[4]
        self.dataLength = bytes[5]

        # standard parameter
        self.resourceId = bytes[6]
        self.oNo = bytes[7]
        self.oPos = bytes[8]
        self.wpNo = bytes[9]
        self.opNo = bytes[10]
        self.bufNo = bytes[11]
        self.bufPos = bytes[12]
        self.carrierId = bytes[13]
        self.palletID = bytes[14]
        self.palletPos = bytes[15]
        self.pNo = bytes[16]
        self.stopperId = bytes[17]
        self.errorStepNo = bytes[18]
        self.stepNo = bytes[19]
        self.maxRecords = bytes[20]
        self.boxId = bytes[21]
        self.boxPos = bytes[22]
        self.mainOPos = bytes[23]
        self.beltNo = bytes[24]
        self.cNo = bytes[25]
        self.boxPNo = bytes[26]
        self.palletPNo = bytes[27]
        self.aux1Int = bytes[28]
        self.aux2Int = bytes[29]
        self.aux1DInt = bytes[30]
        self.aux2DInt = bytes[31]
        self.mainPNo = bytes[32]

        if len(bytes) >= 33:
            for i in range(33, len(bytes)):
                self.serviceParams.append(bytes[i])

    def _encodeBin(self):
        # Header
        msg = str(self.tcpIdent)
        msg += self._parseToEndian(self.requestID, False)
        msg += self._parseToEndian(self.mClass, False)
        msg += self._parseToEndian(self.mNo, False)
        msg += self._parseToEndian(self.errorState, False)
        msg += self._parseToEndian(self.dataLength, False)

        # standardparameter
        msg += self._parseToEndian(self.resourceId, False)
        msg += self._parseToEndian(self.oNo, True)
        msg += self._parseToEndian(self.oPos, False)
        msg += self._parseToEndian(self.wpNo, False)
        msg += self._parseToEndian(self.opNo, False)
        msg += self._parseToEndian(self.bufNo, False)
        msg += self._parseToEndian(self.bufPos, False)
        msg += self._parseToEndian(self.carrierId, False)
        msg += self._parseToEndian(self.palletID, False)
        msg += self._parseToEndian(self.palletPos, False)
        msg += self._parseToEndian(self.pNo, True)
        msg += self._parseToEndian(self.stopperId, False)
        msg += self._parseToEndian(self.errorStepNo, False)
        msg += self._parseToEndian(self.stepNo, False)
        msg += self._parseToEndian(self.maxRecords, False)
        msg += self._parseToEndian(self.boxId, False)
        msg += self._parseToEndian(self.boxPos, False)
        msg += self._parseToEndian(self.mainOPos, False)
        msg += self._parseToEndian(self.beltNo, False)
        msg += self._parseToEndian(self.cNo, True)
        msg += self._parseToEndian(self.boxPNo, True)
        msg += self._parseToEndian(self.palletPNo, True)
        msg += self._parseToEndian(self.aux1Int, False)
        msg += self._parseToEndian(self.aux2Int, False)
        msg += self._parseToEndian(self.aux1DInt, True)
        msg += self._parseToEndian(self.aux2DInt, True)
        msg += self._parseToEndian(self.mainPNo, True)
        # standardparameter bytes reserved
        for item in range(44):
            msg += "00"

        # servicespecific parameter, could be to be parsed diffrently odepending on request
        # encoding for getBufForBufNo
        if self.mClass == 150 and self.mNo == 1:
            msg += self._parseToEndian(self.serviceParams[0], False)
            msg += self._parseToEndian(self.serviceParams[1], False)
            msg += self._parseToEndian(self.serviceParams[2], True)
            msg += self._parseToEndian(self.serviceParams[3], True)
            msg += self._parseToEndian(self.serviceParams[4], False)
        # getUnknownParts
        elif self.mClass == 200 and self.mNo == 5:
            for i in range(math.ceil(len(self.serviceParams)/35)):
                for j in range(35):
                    if j == 0:
                        msg += self._parseToEndian(
                            self.serviceParams[j + 35*i], True)
                    else:
                        if len(self.serviceParams) > (j+35*i):
                            msg += format(self.serviceParams[j + 35*i], "02x")
        elif self.mClass == 100 and self.mNo == 111:
            for i in range(len(self.serviceParams)):
                msg += format(self.serviceParams[i], "02x")
        else:
            for i in range(len(self.serviceParams)):
                msg += self._parseToEndian(self.serviceParams[i], False)

        return msg

    def _decodeBin(self):
        # header
        bytes = list((self.msg[i:i+2] for i in range(0, len(self.msg), 2)))
        self.requestID = self._parseFromEndian(bytes[4:6])
        self.mClass = self._parseFromEndian(bytes[6:8])
        self.mNo = self._parseFromEndian(bytes[8:10])
        self.errorState = self._parseFromEndian(bytes[10:12])
        self.dataLength = self._parseFromEndian(bytes[12:14])

        # standard parameter
        self.resourceId = self._parseFromEndian(bytes[14:16])
        self.oNo = self._parseFromEndian(bytes[16:20])
        self.oPos = self._parseFromEndian(bytes[20:22])
        self.wpNo = self._parseFromEndian(bytes[22:24])
        self.opNo = self._parseFromEndian(bytes[24:26])
        self.bufNo = self._parseFromEndian(bytes[26:28])
        self.bufPos = self._parseFromEndian(bytes[28:30])
        self.carrierId = self._parseFromEndian(bytes[30:32])
        self.palletID = self._parseFromEndian(bytes[32:34])
        self.palletPos = self._parseFromEndian(bytes[34:36])
        self.pNo = self._parseFromEndian(bytes[36:40])
        self.stopperId = self._parseFromEndian(bytes[40:42])
        self.errorStepNo = self._parseFromEndian(bytes[42:44])
        self.stepNo = self._parseFromEndian(bytes[44:46])
        self.maxRecords = self._parseFromEndian(bytes[46:48])
        self.boxId = self._parseFromEndian(bytes[48:50])
        self.boxPos = self._parseFromEndian(bytes[50:52])
        self.mainOPos = self._parseFromEndian(bytes[52:54])
        self.beltNo = self._parseFromEndian(bytes[54:56])
        self.cNo = self._parseFromEndian(bytes[56:60])
        self.boxPNo = self._parseFromEndian(bytes[60:64])
        self.palletPNo = self._parseFromEndian(bytes[64:68])
        self.aux1Int = self._parseFromEndian(bytes[68:70])
        self.aux2Int = self._parseFromEndian(bytes[70:72])
        self.aux1DInt = self._parseFromEndian(bytes[72:76])
        self.aux2DInt = self._parseFromEndian(bytes[76:80])
        self.mainPNo = self._parseFromEndian(bytes[80:84])

        # service-specific parameter
        if len(bytes) != 128:
            # serviceparams is string
            if self.mClass == 100 and self.mNo == 111:
                for i in range(128, len(bytes), 1):
                    self.serviceParams.append(
                        self._parseFromEndian(bytes[i: i+1]))
            # serviceparams are normal bytes
            else:
                for i in range(128, len(bytes), 2):
                    self.serviceParams.append(
                        self._parseFromEndian(bytes[i: i+2]))

    # parses a number to hex in the binary format
    # @params:
    #   number: number to parse
    #   isInt32: if number is int32 (true) or int16(false)
    def _parseToEndian(self, number, isInt32):
        if isInt32:
            hex = format(number, "08x")
        else:
            hex = format(number, "04x")

        binArray = [hex[i:i+2] for i in range(0, len(hex), 2)]
        binStr = ""

        if self.tcpIdent == "33333302":
            for i in range(0, len(binArray), 1):
                binStr += binArray[i]
        elif self.tcpIdent == "33333301":
            for i in range(len(binArray)-1, -1, -1):
                binStr += binArray[i]

        return binStr

    # parses given bytes to number depending if message is in big or little endian
    # @params:
    #   bytes: bytes to parse
    def _parseFromEndian(self, bytes):
        nmbrstr = ""
        if self.tcpIdent == "33333302":
            for i in range(0, len(bytes), 1):
                nmbrstr += bytes[i]
        elif self.tcpIdent == "33333301":
            for i in range(len(bytes)-1, -1, -1):
                nmbrstr += bytes[i]

        return int(nmbrstr, 16)

    # debugging tool which prints all attributes from instance in a readable format
    def _printAttr(self):
        print("tcpIdent: " + str(self.tcpIdent))
        print("requestID: " + str(self.requestID))
        print("mClass: " + str(self.mClass))
        print("mNo: " + str(self.mNo))
        print("errorState: " + str(self.errorState))
        print("dataLength: " + str(self.dataLength))
        print("resourceId: " + str(self.resourceId))
        print("oNo: " + str(self.oNo))
        print("oPos: " + str(self.oPos))
        print("wpNo: " + str(self.wpNo))
        print("opNo: " + str(self.opNo))
        print("bufNo: " + str(self.bufNo))
        print("bufPos: " + str(self.bufPos))
        print("carrierId: " + str(self.carrierId))
        print("palletID: " + str(self.palletID))
        print("palletPos: " + str(self.palletPos))
        print("pNo: " + str(self.pNo))
        print("stopperId: " + str(self.stopperId))
        print("errorStepNo: " + str(self.errorStepNo))
        print("stepNo: " + str(self.stepNo))
        print("maxRecords: " + str(self.maxRecords))
        print("boxId: " + str(self.boxId))
        print("boxPos: " + str(self.boxPos))
        print("mainOPos: " + str(self.mainOPos))
        print("beltNo: " + str(self.beltNo))
        print("cNo: " + str(self.cNo))
        print("boxPNo: " + str(self.boxPNo))
        print("palletPNo: " + str(self.palletPNo))
        print("aux1Int: " + str(self.aux1Int))
        print("aux2Int: " + str(self.aux2Int))
        print("aux1DInt: " + str(self.aux1DInt))
        print("aux2DInt: " + str(self.aux2DInt))
        print("mainPNo: " + str(self.mainPNo))
        print("serviceParams: " + str(self.serviceParams))

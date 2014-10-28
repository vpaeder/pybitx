""""
	Copyright (c) 2014 Vincent Paeder
	
	This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""

"""

    Parser for National Instruments LabView FPGA bitfiles (LVBITX).
    Includes a class to generate compatible XML.
    Note that the signatures won't be generated correctly, but it doesn't seem to be a problem
    (as long as the signature provided to the driver on load is the same as the one in the file).

"""


class Datatype():
    """
    
        Datatype class for Register objects
        
    """
	def __init__(self):
		self.type = 0 # type code (see TypeCode dict)
		self.name = "" # register name

class DatatypeArray():
    """
    
        Datatype array class for Register objects (used to create arrays of subtypes)
        
    """
	def __init__(self):
		self.name = "" # register name
		self.size = 4 # array size
		self.type = Datatype() # subtype (Datatype class)

class Register:
    """
    
        Register informations
    
    """
	def __init__(self):
		self.name = "" # register name
		self.hidden = False # if False, appears in the interface
		self.indicator = False # if True, appears as an indicator in the interface
		self.datatype = Datatype() # register data type (Datatype class)
		self.flattenedType = "" # not sure what this is (works without)
		self.offset = 0 # address offset to be used to access the register with read/write operations
		self.sizeInBits = 0 # register size in bits
		self.classId = 18 # numerical id for datatype(?)
		self.internal = False # if True, is an internal variable
		self.id = 0 # numerical id
		self.bidirectional = True # if True, can be read and written
		self.synchronous = False # synchronous is True
		self.mechanicalAction = 0 # numerical code for mechanical action (see MechanicalActionCode dict)
		self.accessMayTimeout = False #
		self.registerNode = False #

class RegisterBlock():
    """
    
        Register block informations
    
    """
	def __init__(self):
		self.name = "" # register name
		self.offset = 0 # address offset

class DmaDatatype():
    """
    
        Data type class for DMA channels
    
    """
	def __init__(self):
		self.delta = 1.0 # increment delta
		self.integerWordLength = 32 # integer word length
		self.maximum = 1.0 # maximum value
		self.minimum = 0.0 # minimum value
		self.signed = False # signed data type?
		self.subtype = 0 #
		self.wordLength = 0 # word length

class DmaChannel():
    """
    
        DMA channel informations
    
    """
	def __init__(self):
		self.name = "" # channel name
		self.baseAddressTag = "" # address tag
		self.controlSet = 0 #
		self.datatype = DmaDatatype() # data type (DmaDatatype class)
		self.direction = 0 # direction code (see DirectionCode dict)
		self.implementation = 0 # implementation code (see ImplementationCode dict)
		self.number = 0 # numerical id (to be used to access it)
		self.numberOfElements = 0 # number of elements the channel can host
		self.userVisible = True # if True, is visible
		self.writeWindowAddressTag = "" # address tag for a P2P FIFO
		self.writeWindowSize = 0 # number of elements for a P2P FIFO

class BaseClock():
    """
    
        Base clock class
    
    """
	def __init__(self):
		self.name = "" # clock name

class Icon():
    """
    
        Labview icon class
    
    """
	def __init__(self):
		self.imageType = 0 # image type
		self.imageDepth = 8 # image depth
		self.image = "" # image string (base64 encoded)
		self.mask = "" # image transparence mask (base64 encoded)
		self.colors = "" # image colors (base64 encoded)
		self.rectangle = [0,0,0,0] # image rectange [top, left, bottom, right]

TypeCode = {u"Bool":0, u"I8":1, u"U8":2, u"I16":3, u"U16":4, u"I32":5, u"U32":6, u"I64":7, u"U64":8,u"Array":9}
DirectionCode = {u"TargetToHost":0, u"HostToTarget":1}
MechanicalActionCode = {u"Switch When Pressed":0, u"Switch When Released":1, u"Switch Until Released":2, u"Latch When Pressed":3, u"Latch When Released":4, u"Latch Until Released":5}
ImplementationCode = {u"niFpgaPeerToPeerReader":0, u"niFpgaPeerToPeerWriter":1, u"niFpgaTargetToHost":2, u"niFpgaHostToTarget":3}

class LVbitxParse:
    """
    
        LVBITX parser class
    
    """
	def __init__(self, fileName=""):
        """
        
            Initialization.
            
            Parameters:
                fileName        LVBITX file name (str, optional)
        
        """
		self.bitx = None
		if fileName!="":
			self.OpenFile(fileName)
	
	def OpenFile(self, fileName):
        """
        
            Opens LVBITX file.
            
            Parameters:
                fileName        LVBITX file name (str)
        
        """
		from xml.dom import minidom
		try:
			self.bitx = minidom.parse(fileName)
		except:
			self.bitx = None
	
	def GetSignature(self):
        """
        
            Reads signature for SignatureRegister of loaded file.
            
            Output:
                file signature (str)
            
        """
		if self.bitx!=None:
			try:
				sig = str(self.bitx.getElementsByTagName("SignatureRegister")[0].childNodes[0].data)
				return sig
			except:
				return ""
	
	def GetViName(self):
        """
        
            Reads VI name associated to loaded file.
            
            Output:
                VI name (str)
            
        """
		if self.bitx!=None:
			for x in self.bitx.getElementsByTagName("VI")[0].childNodes:
				if x.tagName == u"Name":
					return x.childNodes[0].data
		return ""
	
	def GetRegisterList(self):
        """
        
            Extracts register list from loaded file.
            
            Output:
                list of Register objects
            
        """
		regList = []
		if self.bitx!=None:
			for x in self.bitx.getElementsByTagName("RegisterList")[0].childNodes:
				if hasattr(x,"tagName") and x.tagName == u"Register":
					reg = Register()
					for y in x.childNodes:
						if hasattr(y,'tagName') and y.tagName == u"Name": reg.name = y.childNodes[0].data
						if hasattr(y,'tagName') and y.tagName == u"Hidden": reg.hidden = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"Indicator": reg.indicator = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"Datatype":
							for z in y.childNodes:
								if hasattr(z,'getElementsByTagName'):
									if z.tagName==u"Array":
										dtype = DatatypeArray()
										if len(z.getElementsByTagName("Name")[0].childNodes)>0: dtype.name = z.getElementsByTagName("Name")[0].childNodes[0].data
										dtype.size = int(z.getElementsByTagName("Size")[0].childNodes[0].data)
										for zz in z.getElementsByTagName("Type")[0].childNodes:
											if hasattr(zz,"tagName"):
												dtype.type.type = TypeCode[zz.tagName]
												if len(zz.getElementsByTagName("Name")[0].childNodes)>0: dtype.type.name = zz.getElementsByTagName("Name")[0].childNodes[0].data
									else:
										dtype = Datatype()
										if len(z.getElementsByTagName("Name")[0].childNodes)>0: dtype.name = z.getElementsByTagName("Name")[0].childNodes[0].data
										dtype.type = TypeCode[z.tagName]
									reg.datatype = dtype
						if hasattr(y,'tagName') and y.tagName == u"FlattenedType" and len(y.childNodes)>0: reg.flattenedType = y.childNodes[0].data
						if hasattr(y,'tagName') and y.tagName == u"Offset": reg.offset = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"SizeInBits": reg.sizeInBits = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"Class": reg.classId = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"Internal": reg.internal = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"ID": reg.id = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"Bidirectional": reg.bidirectional = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"Synchronous": reg.synchronous = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"MechanicalAction": reg.mechanicalAction = MechanicalActionCode[y.childNodes[0].data]
						if hasattr(y,'tagName') and y.tagName == u"AccessMayTimeout": reg.accessMayTimeout = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"RegisterNode": reg.registerNode = y.childNodes[0].data == u"true"
					regList.append(reg)
			return regList
	
	def GetDmaChannels(self):
        """
        
            Reads DMA channels from loaded file.
            
            Output:
                list of DmaChannel objects
            
        """
		channels = []
		if self.bitx!=None:
			for x in self.bitx.getElementsByTagName("DmaChannelAllocationList")[0].childNodes:
				if hasattr(x,'tagName') and x.tagName == u"Channel":
					chan = DmaChannel()
					chan.name = x.attributes["name"].value
					for y in x.childNodes:
						if hasattr(y,'tagName') and y.tagName == u"BaseAddressTag": chan.baseAddressTag = y.childNodes[0].data
						if hasattr(y,'tagName') and y.tagName == u"ControlSet": chan.controlSet = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"DataType":
							dtype = DmaDatatype()
							for z in y.childNodes:
								if hasattr(z,'tagName') and z.tagName == u"Delta": dtype.delta = float(z.childNodes[0].data)
								if hasattr(z,'tagName') and z.tagName == u"IntegerWordLength": dtype.integerWordLength = int(z.childNodes[0].data)
								if hasattr(z,'tagName') and z.tagName == u"Maximum": dtype.maximum = float(z.childNodes[0].data)
								if hasattr(z,'tagName') and z.tagName == u"Minimum": dtype.minimum = float(z.childNodes[0].data)
								if hasattr(z,'tagName') and z.tagName == u"Signed": dtype.signed = z.childNodes[0].data == u"true"
								if hasattr(z,'tagName') and z.tagName == u"SubType": dtype.subtype = TypeCode[z.childNodes[0].data]
								if hasattr(z,'tagName') and z.tagName == u"WordLength": dtype.wordLength = int(z.childNodes[0].data)
							chan.datatype = dtype
						if hasattr(y,'tagName') and y.tagName == u"Direction": chan.direction = DirectionCode[y.childNodes[0].data]
						if hasattr(y,'tagName') and y.tagName == u"Implementation": chan.implementation = ImplementationCode[y.childNodes[0].data]
						if hasattr(y,'tagName') and y.tagName == u"Number": chan.number = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"NumberOfElements": chan.numberOfElements = int(y.childNodes[0].data)
						if hasattr(y,'tagName') and y.tagName == u"UserVisible": chan.userVisible = y.childNodes[0].data == u"true"
						if hasattr(y,'tagName') and y.tagName == u"WriteWindowAddressTag": chan.writeWindowAddressTag = y.childNodes[0].data
						if hasattr(y,'tagName') and y.tagName == u"WriteWindowSize": chan.writeWindowSize = int(y.childNodes[0].data)
					channels.append(chan)
		return channels
	
	def GetRegisterBlocks(self):
        """
        
            Reads register blocks from loaded file.
            
            Output:
                list of RegisterBlock objects
            
        """
		blocks = []
		if self.bitx!=None:
			for x in self.bitx.getElementsByTagName("RegisterBlockList")[0].childNodes:
				if hasattr(x,'tagName') and x.tagName == u"RegisterBlock":
					reg = RegisterBlock()
					reg.name = x.attributes["name"].value
					for y in x.childNodes:
						if hasattr(y,'tagName') and y.tagName == u"Offset": reg.offset = int(y.childNodes[0].data,16)
					blocks.append(reg)
		return blocks
	
	def GetUsedBaseClocks(self):
        """
        
            Reads used base clocks from loaded file.
            
            Output:
                list of BaseClock objects
            
        """
		clocks = []
		if self.bitx!=None:
			for x in self.bitx.getElementsByTagName("UsedBaseClockList")[0].childNodes:
				if hasattr(x,'tagName') and x.tagName == u"BaseClock":
					bc = BaseClock()
					bc.name = x.attributes["name"].value
					clocks.append(bc)
		return clocks
	
	def GetBitstream(self):
        """
        
            Reads bitstream from loaded file.
            
            Output:
                decoded binary bitstream (str)
            
        """
	    if self.bitx!=None:
            import base64
            return base64.b64decode(self.bitx.getElementsByTagName("Bitstream")[0].childNodes[0].data)
        else:
            return ""
	

class LVBitxCreate():
    """
    
        LVBITX creator class
    
    """
	def __init__(self):
        """
        
            Initialization.
            
        """
		self.signatureRegister = "" # signature to be provided on load
		self.signatureGuids = "" # ?
		self.signatureNames = "" # ?
		self.viName = "default.vi" # VI name
		self.targetClass = "PXIe-7965R" # target class
		self.autoRunWhenDownloaded = False # if True, auto-run when loaded
		self.multipleUserClocks = False # if True, more than one clock is defined
		self.bitstream = "" # binary bitstream
		self.registers = [] # list of Register objects
		self.icon = Icon() # VI icon object
		self.channels = [] # list of DmaChannel objects
		self.registerBlocks = [] # list of RegisterBlock objects
		self.usedBaseClocks = [] # list of BaseClock objects

	def Generate(self):
        """
        
            Generates a LVBITX stream from the properties of the object.
            
            Output:
                string containing LVBITX data (str)
        
        """
		from xml.dom import minidom
		doc = minidom.Document()
		root = doc.createElement("Bitfile")
		doc.appendChild(root)
		
		# bitfile version tag
		bfVersion = doc.createElement("BitfileVersion")
		bfVersionText = doc.createTextNode("1.0")
		bfVersion.appendChild(bfVersionText)
		root.appendChild(bfVersion)
		
		# SignatureRegister tag
		sigRegister = doc.createElement("SignatureRegister")
		sigRegisterText = doc.createTextNode(self.signatureRegister)
		sigRegister.appendChild(sigRegisterText)
		root.appendChild(sigRegister)
		
		# SignatureGuids tag
		sigGuids = doc.createElement("SignatureGuids")
		sigGuidsText = doc.createTextNode(self.signatureGuids)
		sigGuids.appendChild(sigGuidsText)
		root.appendChild(sigGuids)
		
		# SignatureNames tag
		sigNames = doc.createElement("SignatureNames")
		sigNamesText = doc.createTextNode(self.signatureNames)
		sigNames.appendChild(sigNamesText)
		root.appendChild(sigNames)
		
		# TimeStamp tag
		from datetime import datetime
		timeStamp = doc.createElement("TimeStamp")
		timeStampText = doc.createTextNode(datetime.today().strftime("%m/%d/%Y%l:%M %p"))
		timeStamp.appendChild(timeStampText)
		root.appendChild(timeStamp)
		
		# CompilationStatus tag
		compStatus = doc.createElement("CompilationStatus")
		compStatusText = doc.createTextNode("")
		compStatus.appendChild(compStatusText)
		root.appendChild(compStatus)
		
		# BitstreamVersion tag
		bsVersion = doc.createElement("BitstreamVersion")
		bsVersionText = doc.createTextNode("2")
		bsVersion.appendChild(bsVersionText)
		root.appendChild(bsVersion)
		
		# VI node
		viNode = doc.createElement("VI")
		root.appendChild(viNode)
		
		# VI name tag
		viName = doc.createElement("Name")
		viNameText = doc.createTextNode(self.viName)
		viName.appendChild(viNameText)
		viNode.appendChild(viName)
		
		# register list node
		registerList = doc.createElement("RegisterList")
		viNode.appendChild(registerList)
		for reg in self.registers:
			register = doc.createElement("Register")
			registerList.appendChild(register)
			# name tag
			registerName = doc.createElement("Name")
			registerNameText = doc.createTextNode(reg.name)
			registerName.appendChild(registerNameText)
			register.appendChild(registerName)
			# hidden tag
			registerHidden = doc.createElement("Hidden")
			registerHiddenText = doc.createTextNode(str(reg.hidden).lower())
			registerHidden.appendChild(registerHiddenText)
			register.appendChild(registerHidden)
			
			# indicator tag
			registerIndicator = doc.createElement("Indicator")
			registerIndicatorText = doc.createTextNode(str(reg.indicator).lower())
			registerIndicator.appendChild(registerIndicatorText)
			register.appendChild(registerIndicator)
			
			# data type tag
			registerDatatype = doc.createElement("DataType")
			register.appendChild(registerDatatype)
			
			if isinstance(reg.datatype,Datatype):
				registerTypeCode = doc.createElement(TypeCode.keys()[TypeCode.values().index(reg.datatype.type)])
				registerDatatype.appendChild(registerTypeCode)
				registerTypeName = doc.createElement("Name")
				registerTypeCode.appendChild(registerTypeName)
				registerTypeNameText = doc.createTextNode(reg.datatype.name)
				registerTypeName.appendChild(registerTypeNameText)
			elif isinstance(reg.datatype,DatatypeArray):
				# array name
				registerTypeName = doc.createElement("Name")
				registerDatatype.appendChild(registerTypeName)
				registerTypeNameText = doc.createTextNode(reg.datatype.name)
				registerTypeName.appendChild(registerTypeNameText)
				# array size
				registerTypeSize = doc.createElement("Size")
				registerDatatype.appendChild(registerTypeSize)
				registerTypeSizeText = doc.createTextNode(str(reg.datatype.size))
				registerTypeSize.appendChild(registerTypeSizeText)
				# array type
				registerArrayType = doc.createElement("Type")
				registerDatatype.appendChild(registerArrayType)
				registerTypeCode = doc.createElement(TypeCode.keys()[TypeCode.values().index(reg.datatype.type.type)])
				registerArrayType.appendChild(registerTypeCode)
				# array type name
				registerArrayTypeName = doc.createElement("Name")
				registerTypeCode.appendChild(registerArrayTypeName)
				registerArrayTypeNameText = doc.createTextNode(reg.datatype.type.name)
				registerArrayTypeName.appendChild(registerArrayTypeNameText)
			
			# flattened type tag
			registerFlattenedType = doc.createElement("FlattenedType")
			registerFlattenedTypeText = doc.createTextNode(reg.flattenedType)
			registerFlattenedType.appendChild(registerFlattenedTypeText)
			register.appendChild(registerFlattenedType)
			
			# grouping tag
			registerGrouping = doc.createElement("Grouping")
			register.appendChild(registerGrouping)
			
			# offset tag
			registerOffset = doc.createElement("Offset")
			registerOffsetText = doc.createTextNode(str(reg.offset))
			registerOffset.appendChild(registerOffsetText)
			register.appendChild(registerOffset)
			
			# size in bits tag
			registerSizeInBits = doc.createElement("SizeInBits")
			registerSizeInBitsText = doc.createTextNode(str(reg.sizeInBits))
			registerSizeInBits.appendChild(registerSizeInBitsText)
			register.appendChild(registerSizeInBits)
			
			# class tag
			registerClass = doc.createElement("Class")
			registerClassText = doc.createTextNode(str(reg.classId))
			registerClass.appendChild(registerClassText)
			register.appendChild(registerClass)
			
			# internal tag
			registerInternal = doc.createElement("Internal")
			registerInternalText = doc.createTextNode(str(reg.internal).lower())
			registerInternal.appendChild(registerInternalText)
			register.appendChild(registerInternal)
			
			# typedef path tag
			registerTypedefPath = doc.createElement("TypedefPath")
			register.appendChild(registerTypedefPath)
			
			# id tag
			registerID = doc.createElement("ID")
			registerIDText = doc.createTextNode(str(reg.id))
			registerID.appendChild(registerIDText)
			register.appendChild(registerID)
			
			# bidirectional tag
			registerBidirectional = doc.createElement("Bidirectional")
			registerBidirectionalText = doc.createTextNode(str(reg.bidirectional).lower())
			registerBidirectional.appendChild(registerBidirectionalText)
			register.appendChild(registerBidirectional)
			
			# synchronous tag
			registerSynchronous = doc.createElement("Synchronous")
			registerSynchronousText = doc.createTextNode(str(reg.synchronous).lower())
			registerSynchronous.appendChild(registerSynchronousText)
			register.appendChild(registerSynchronous)
			
			# mechanical action tag
			registerMechanicalAction = doc.createElement("MechanicalAction")
			registerMechanicalActionText = doc.createTextNode(MechanicalActionCode.keys()[MechanicalActionCode.values().index(reg.mechanicalAction)])
			registerMechanicalAction.appendChild(registerMechanicalActionText)
			register.appendChild(registerMechanicalAction)
			
			# AccessMayTimeout tag
			registerAccessMayTimeout = doc.createElement("AccessMayTimeout")
			registerAccessMayTimeoutText = doc.createTextNode(str(reg.accessMayTimeout).lower())
			registerAccessMayTimeout.appendChild(registerAccessMayTimeoutText)
			register.appendChild(registerAccessMayTimeout)
			
			# RegisterNode tag
			registerRegisterNode = doc.createElement("RegisterNode")
			registerRegisterNodeText = doc.createTextNode(str(reg.registerNode).lower())
			registerRegisterNode.appendChild(registerRegisterNodeText)
			register.appendChild(registerRegisterNode)
		
			# subcontrol list tag
			registerSubControlList = doc.createElement("SubControlList")
			register.appendChild(registerSubControlList)
			
		
		# icon node
		iconNode = doc.createElement("Icon")
		root.appendChild(iconNode)
		
		# ImageType tag
		iconImageType = doc.createElement("ImageType")
		iconImageTypeText = doc.createTextNode(str(self.icon.imageType))
		iconImageType.appendChild(iconImageTypeText)
		iconNode.appendChild(iconImageType)
		
		# ImageDepth tag
		iconImageDepth = doc.createElement("ImageDepth")
		iconImageDepthText = doc.createTextNode(str(self.icon.imageDepth))
		iconImageDepth.appendChild(iconImageDepthText)
		iconNode.appendChild(iconImageDepth)
		
		# Image tag
		iconImage = doc.createElement("Image")
		iconImageText = doc.createTextNode(self.icon.image)
		iconImage.appendChild(iconImageText)
		iconNode.appendChild(iconImage)
		
		# Mask tag
		iconMask = doc.createElement("Mask")
		iconMaskText = doc.createTextNode(self.icon.mask)
		iconMask.appendChild(iconMaskText)
		iconNode.appendChild(iconMask)
		
		# Colors tag
		iconColors = doc.createElement("Colors")
		iconColorsText = doc.createTextNode(self.icon.colors)
		iconColors.appendChild(iconColorsText)
		iconNode.appendChild(iconColors)
		
		# Rectangle node
		iconRectangle = doc.createElement("Rectangle")
		iconNode.appendChild(iconRectangle)
		iconRectangleLeft = doc.createElement("Left")
		iconRectangleLeftText = doc.createTextNode(str(self.icon.rectangle[0]))
		iconRectangleLeft.appendChild(iconRectangleLeftText)
		iconRectangle.appendChild(iconRectangleLeft)
		iconRectangleTop = doc.createElement("Top")
		iconRectangleTopText = doc.createTextNode(str(self.icon.rectangle[1]))
		iconRectangleTop.appendChild(iconRectangleTopText)
		iconRectangle.appendChild(iconRectangleTop)
		iconRectangleRight = doc.createElement("Right")
		iconRectangleRightText = doc.createTextNode(str(self.icon.rectangle[2]))
		iconRectangleRight.appendChild(iconRectangleRightText)
		iconRectangle.appendChild(iconRectangleRight)
		iconRectangleBottom = doc.createElement("Bottom")
		iconRectangleBottomText = doc.createTextNode(str(self.icon.rectangle[3]))
		iconRectangleBottom.appendChild(iconRectangleBottomText)
		iconRectangle.appendChild(iconRectangleBottom)
		
		# Project node
		projectNode = doc.createElement("Project")
		root.appendChild(projectNode)
		
		# TargetClass tag
		targetClass = doc.createElement("TargetClass")
		targetClassText = doc.createTextNode(self.targetClass)
		targetClass.appendChild(targetClassText)
		projectNode.appendChild(targetClass)
		
		# AutoRunWhenDownloaded tag
		autoRunWhenDownloaded = doc.createElement("AutoRunWhenDownloaded")
		autoRunWhenDownloadedText = doc.createTextNode(str(self.autoRunWhenDownloaded).lower())
		autoRunWhenDownloaded.appendChild(autoRunWhenDownloadedText)
		projectNode.appendChild(autoRunWhenDownloaded)
		
		# Compilation results tree
		compTree = doc.createElement("CompilationResultsTree")
		projectNode.appendChild(compTree)
		compResults = doc.createElement("CompilationResults")
		compTree.appendChild(compResults)
		
		# NiFlexRio
		niFlexRio = doc.createElement("NiFlexRio")
		compResults.appendChild(niFlexRio)
		puma2 = doc.createElement("Puma2")
		niFlexRio.appendChild(puma2)
		pumaBsVersion = doc.createElement("BitstreamVersion")
		pumaBsVersionText = doc.createTextNode("2")
		pumaBsVersion.appendChild(pumaBsVersionText)
		puma2.appendChild(pumaBsVersion)
		
		# NiFpga
		niFpga = doc.createElement("NiFpga")
		compResults.appendChild(niFpga)
		
		# DmaChannelAllocationList tag
		dmaChannelAllocationList = doc.createElement("DmaChannelAllocationList")
		compResults.appendChild(dmaChannelAllocationList)
		for chan in self.channels:
			channel = doc.createElement("Channel")
			channel.setAttribute("name",chan.name)
			dmaChannelAllocationList.appendChild(channel)
			
			# BaseAddressTag tag
			chanBaseAddressTag = doc.createElement("BaseAddressTag")
			chanBaseAddressTagText = doc.createTextNode(chan.baseAddressTag)
			chanBaseAddressTag.appendChild(chanBaseAddressTagText)
			channel.appendChild(chanBaseAddressTag)
		
			# ControlSet tag
			chanControlSet = doc.createElement("ControlSet")
			chanControlSetText = doc.createTextNode(str(chan.controlSet))
			chanControlSet.appendChild(chanControlSetText)
			channel.appendChild(chanControlSet)
			
			# Datatype tag
			channelDatatype = doc.createElement("DataType")
			channel.appendChild(channelDatatype)
			
			# Datatype delta tag
			chanDtypeDelta = doc.createElement("Delta")
			chanDtypeDeltaText = doc.createTextNode(str(chan.datatype.delta))
			chanDtypeDelta.appendChild(chanDtypeDeltaText)
			channelDatatype.appendChild(chanDtypeDelta)
			
			# Datatype IntegerWordLength tag
			chanDtypeIntegerWordLength = doc.createElement("IntegerWordLength")
			chanDtypeIntegerWordLengthText = doc.createTextNode(str(chan.datatype.integerWordLength))
			chanDtypeIntegerWordLength.appendChild(chanDtypeIntegerWordLengthText)
			channelDatatype.appendChild(chanDtypeIntegerWordLength)
			
			# Datatype Maximum tag
			chanDtypeMaximum = doc.createElement("Maximum")
			chanDtypeMaximumText = doc.createTextNode(str(chan.datatype.maximum))
			chanDtypeMaximum.appendChild(chanDtypeMaximumText)
			channelDatatype.appendChild(chanDtypeMaximum)
			
			# Datatype Minimum tag
			chanDtypeMinimum = doc.createElement("Minimum")
			chanDtypeMinimumText = doc.createTextNode(str(chan.datatype.minimum))
			chanDtypeMinimum.appendChild(chanDtypeMinimumText)
			channelDatatype.appendChild(chanDtypeMinimum)
			
			# Datatype Signed tag
			chanDtypeSigned = doc.createElement("Signed")
			chanDtypeSignedText = doc.createTextNode(str(chan.datatype.signed).lower())
			chanDtypeSigned.appendChild(chanDtypeSignedText)
			channelDatatype.appendChild(chanDtypeSigned)
			
			# Datatype SubType tag
			chanDtypeSubType = doc.createElement("SubType")
			chanDtypeSubTypeText = doc.createTextNode(TypeCode.keys()[TypeCode.values().index(chan.datatype.subtype)])
			chanDtypeSubType.appendChild(chanDtypeSubTypeText)
			channelDatatype.appendChild(chanDtypeSubType)
			
			# Datatype WordLength tag
			chanDtypeWordLength = doc.createElement("WordLength")
			chanDtypeWordLengthText = doc.createTextNode(str(chan.datatype.wordLength))
			chanDtypeWordLength.appendChild(chanDtypeWordLengthText)
			channelDatatype.appendChild(chanDtypeWordLength)
			
			# Implementation tag
			chanImplementation = doc.createElement("Implementation")
			chanImplementationText = doc.createTextNode(ImplementationCode.keys()[ImplementationCode.values().index(chan.implementation)])
			chanImplementation.appendChild(chanImplementationText)
			channel.appendChild(chanImplementation)
			
			# Number tag
			chanNumber = doc.createElement("Number")
			chanNumberText = doc.createTextNode(str(chan.number))
			chanNumber.appendChild(chanNumberText)
			channel.appendChild(chanNumber)
			
			# NumberOfElements tag
			chanNumberOfElements = doc.createElement("NumberOfElements")
			chanNumberOfElementsText = doc.createTextNode(str(chan.numberOfElements))
			chanNumberOfElements.appendChild(chanNumberOfElementsText)
			channel.appendChild(chanNumberOfElements)
			
			# UserVisible tag
			chanUserVisible = doc.createElement("UserVisible")
			chanUserVisibleText = doc.createTextNode(str(chan.userVisible).lower())
			chanUserVisible.appendChild(chanUserVisibleText)
			channel.appendChild(chanUserVisible)
		
		# RegisterBlockList tag
		registerBlockList = doc.createElement("RegisterBlockList")
		compResults.appendChild(registerBlockList)
		for reg in self.registerBlocks:
			register = doc.createElement("RegisterBlock")
			register.setAttribute("name",reg.name)
			registerBlockList.appendChild(register)
			
			# Offset tag
			regOffset = doc.createElement("Offset")
			regOffsetText = doc.createTextNode(hex(reg.offset))
			regOffset.appendChild(regOffsetText)
			register.appendChild(regOffset)
		
		# UsedBaseClockList tag
		usedBaseClockList = doc.createElement("UsedBaseClockList")
		compResults.appendChild(usedBaseClockList)
		for clk in self.usedBaseClocks:
			clock = doc.createElement("BaseClock")
			clock.setAttribute("name",clk.name)
			clockText = doc.createTextNode("")
			clock.appendChild(clockText)
			usedBaseClockList.appendChild(clock)
		
		# NIFPGA version tag
		niFpgaVersion = doc.createElement("version")
		niFpgaVersionText = doc.createTextNode("1")
		niFpgaVersion.appendChild(niFpgaVersionText)
		niFpga.appendChild(niFpgaVersion)
		
		# MultipleUserClocks tag
		multipleUserClocks = doc.createElement("MultipleUserClocks")
		multipleUserClocksText = doc.createTextNode(str(self.multipleUserClocks).lower())
		multipleUserClocks.appendChild(multipleUserClocksText)
		projectNode.appendChild(multipleUserClocks)
		
		# ClientData tag
		clientData = doc.createElement("ClientData")
		root.appendChild(clientData)
		
		# Bitstream tag
        import base64
		bitstream = doc.createElement("Bitstream")
		bitstreamText = doc.createTextNode(base64.base64encode(self.bitstream))
		bitstream.appendChild(bitstreamText)
		root.appendChild(bitstream)
		
		return root.toprettyxml()
		
#lvc = LVBitxCreate()
#lvc.registers.append(Register())
#lvc.registers[0].datatype = DatatypeArray()
#lvc.channels.append(DmaChannel())
#lvc.registerBlocks.append(RegisterBlock())
#lvc.usedBaseClocks.append(BaseClock())

#lvp = LVbitxParse()
#lvp.OpenFile("NiFpga_niScopeEXP2PInterleavedDataFPGA.lvbitx")
#lvc.registers = lvp.GetRegisterList()
#lvc.channels = lvp.GetDmaChannels()
#lvc.registerBlocks = lvp.GetRegisterBlocks()
#lvc.usedBaseClocks = lvp.GetUsedBaseClocks()

#print lvc.Generate()

pybitx
======

LabView FPGA bitfile parser.

This is a Python parser class for LabView FPGA bitfiles (lvbitx). It also includes a creator class, which can be used to modify existing bitfiles (creation from scratch may be possible in theory but hasn't been tested).

Architecture
============

Here is a brief overview of the hierarchy of the included classes. Have a look at the inline documentation for a detailed description of each item.

Parser class:
**LVbitxParse**
* __init__(fileName="")
* OpenFile(fileName)
* str GetSignature()
* str GetViName()
* list GetRegisterList()
* list GetDmaChannels()
* list GetRegisterBlocks()
* list GetUsedBaseClocks()
* str GetBitstream()

**LVbitxCreate**
* __init__()
* str Generate()

Not detailed here are the object classes for registers, DMA channels, ...

Usage examples
==============

Parse a file for informations:
	lvp = LVbitxParse()
	lvp.OpenFile("NiFpga_niScopeEXP2PInterleavedDataFPGA.lvbitx")
	regList = lvp.GetRegisterList()
	dmaChannels = lvp.GetDmaChannels()
	regBlocks = lvp.GetRegisterBlocks()
	baseClocks = lvp.GetUsedBaseClocks()
	signature = lvp.GetSignature()
	bitstream = lvp.GetBitstream()

Modify some informations in a file:
	lvp = LVbitxParse()
	lvc = LVbitxCreate()
	lvp.OpenFile("NiFpga_niScopeEXP2PInterleavedDataFPGA.lvbitx")
	lvc.registers = lvp.GetRegisterList()
	lvc.channels = lvp.GetDmaChannels()
	lvc.registerBlocks = lvp.GetRegisterBlocks()
	lvc.usedBaseClocks = lvp.GetUsedBaseClocks()
	lvc.channels[0].name = "NewChannelName"
	lvc.signatureRegister = lvp.GetSignature()
	output = lvc.Generate()

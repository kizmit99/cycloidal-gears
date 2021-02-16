#Author-Frances O'Leary January 2021
#Description-Fusion script with a GUI to generate 3 bodies: cycloidal disk, base plate, and cam based on input parameters.
#ModifiedBy-kizmit99 February 2021 to generate from different parameters

import adsk.core, adsk.fusion, traceback, math

_app = None
_ui  = None

# command inputs
fixedPinRingDiameter = adsk.core.ValueCommandInput.cast(None)
fixedPinDiameter = adsk.core.ValueCommandInput.cast(None)
fixedPinNumber = adsk.core.ValueCommandInput.cast(None)
eccentricity = adsk.core.ValueCommandInput.cast(None)
outputPinRingDiameter = adsk.core.ValueCommandInput.cast(None)
outputPinDiameter = adsk.core.ValueCommandInput.cast(None)
outputPinNumber = adsk.core.ValueCommandInput.cast(None)
camR = adsk.core.ValueCommandInput.cast(None)
centerPinR = adsk.core.ValueCommandInput.cast(None)
camTolerance = adsk.core.ValueCommandInput.cast(None)
baseHeight = adsk.core.ValueCommandInput.cast(None)
pinHeight = adsk.core.ValueCommandInput.cast(None)
camHeight = adsk.core.ValueCommandInput.cast(None)
diskHeight = adsk.core.ValueCommandInput.cast(None)

# global set of event handlers to keep them referenced for the duration of the command
_handlers = []

# event handler that reacts to any changes the user makes to any of the command inputs.
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# event handler that reacts to when the command is destroyed. This terminates the script.            
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# event handler that reacts when the command definition is executed which
# results in the command being created and this event being fired.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            cmd = adsk.core.Command.cast(args.command)
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)        
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)    
            inputs = cmd.commandInputs
            global fixedPinRingDiameter, fixedPinDiameter, fixedPinNumber, eccentricity, outputPinRingDiameter, outputPinDiameter, outputPinNumber, camR, centerPinR, camTolerance, baseHeight, pinHeight, camHeight, diskHeight

            # add inputs
            inputs.addImageCommandInput('image', '', "resources/diagram.png")
            message = '<div align="center">View the documentation <a href="https://github.com/olearyf/cycloidal-gears">here.</a></div>'
            inputs.addTextBoxCommandInput('fullWidth_textBox', '', message, 1, True)            
            fixedPinRingDiameter = inputs.addValueInput('fixedPinRingDiameter', 'Fixed Pin Ring Diameter', 'cm', adsk.core.ValueInput.createByReal(5.0))
            fixedPinDiameter = inputs.addValueInput('fixedPinDiameter', 'Fixed Pin Diameter', 'cm', adsk.core.ValueInput.createByReal(0.5))
            fixedPinNumber = inputs.addValueInput('fixedPinNumber', 'Number of Fixed Pins', '', adsk.core.ValueInput.createByReal(10))
            eccentricity = inputs.addValueInput('eccentricity', 'Eccentricity', '', adsk.core.ValueInput.createByReal(0.125))
            outputPinRingDiameter = inputs.addValueInput('outputPinRingDiameter', 'Output Pin Ring Diameter', '', adsk.core.ValueInput.createByReal(3.0))
            outputPinDiameter = inputs.addValueInput('outputPinDiameter', 'Output Pin Diameter', '', adsk.core.ValueInput.createByReal(0.3))
            outputPinNumber = inputs.addValueInput('outputPinNumber', 'Number of Output Pins', '', adsk.core.ValueInput.createByReal(6))
            camR = inputs.addValueInput('camR', 'Cam Radius', 'cm', adsk.core.ValueInput.createByReal(1.0))
            centerPinR = inputs.addValueInput('centerPinR', 'Center Pin Radius', 'cm', adsk.core.ValueInput.createByReal(0.15))
            camTolerance = inputs.addValueInput('camTolerance', 'Cam Tolerance', 'cm', adsk.core.ValueInput.createByReal(0.05))
            baseHeight = inputs.addValueInput('baseHeight', 'Base Height', 'cm', adsk.core.ValueInput.createByReal(0.5))
            pinHeight = inputs.addValueInput('pinHeight', 'Pin Height', 'cm', adsk.core.ValueInput.createByReal(0.5))
            camHeight = inputs.addValueInput('camHeight', 'Cam Height', 'cm', adsk.core.ValueInput.createByReal(0.5))
            diskHeight = inputs.addValueInput('diskHeight', 'Disk Height', 'cm', adsk.core.ValueInput.createByReal(0.5))

            onExecute = CycloidalGearCommandExecuteHandler()
            cmd.execute.add(onExecute)
            _handlers.append(onExecute) 
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface
        cmdDef = _ui.commandDefinitions.itemById('cmdInputsCyclGear')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdInputsCyclGear', 'My Cycloidal Gear', 'Creates a cycloidal gear based on input parameters.')
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)
        cmdDef.execute()
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

class CycloidalGearCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global fixedPinRingDiameter, fixedPinDiameter, fixedPinNumber, eccentricity, outputPinRingDiameter, outputPinDiameter, outputPinNumber, camR, centerPinR, camTolerance, baseHeight, pinHeight, camHeight, diskHeight
            eventArgs = adsk.core.CommandEventArgs.cast(args)

            fixedPinRingDiameter = fixedPinRingDiameter.value
            fixedPinDiameter = fixedPinDiameter.value
            fixedPinNumber = int(fixedPinNumber.value)
            eccentricity = eccentricity.value
            maxE = (fixedPinRingDiameter / (2 * fixedPinNumber))
            if (eccentricity > maxE):
                eccentricity = maxE
            outputPinRingDiameter = outputPinRingDiameter.value
            outputPinDiameter = outputPinDiameter.value
            outputPinNumber = int(outputPinNumber.value)
            camR = camR.value
            centerPinR = centerPinR.value
            camTolerance = camTolerance.value
            baseHeight = baseHeight.value
            pinHeight = pinHeight.value
            camHeight = camHeight.value
            diskHeight = diskHeight.value

            app = adsk.core.Application.get()
            ui = app.userInterface
            doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
            design = app.activeProduct
            model = design.activeComponent
            features = model.features
            combineFeatures = features.combineFeatures
            rootComp = design.rootComponent
            extrudes = rootComp.features.extrudeFeatures
            sketches = rootComp.sketches
            xyPlane = rootComp.xYConstructionPlane
            drawCycloidalBodies(combineFeatures, app, xyPlane, sketches, extrudes, fixedPinRingDiameter, fixedPinDiameter, fixedPinNumber, eccentricity, outputPinRingDiameter, outputPinDiameter, outputPinNumber, camR, centerPinR, camTolerance, baseHeight, pinHeight, camHeight, diskHeight)
        except:
            if _ui:
                _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

# generates the cycloidal disk, cam, and base plate with pins
def drawCycloidalBodies(combineFeatures, app, xyPlane, sketches, extrudes, fixedD, fixedDp, fixedN, eccentricity, outputD, outputDp, outputN, shaftR, centerpinR, tolerance, baseHeight, pinHeight, camHeight, diskHeight):
    # further calculations
    rollingD = ((fixedN - 1) / fixedN) * fixedD
    rollingR = rollingD / 2
    sigma = fixedD / fixedN
    effectiveR = rollingR + (sigma / 2)

    # create sketches and tools/collections
    diskSketch = sketches.add(xyPlane)
    diskSketch.name = 'diskSketch'
    baseSketch = sketches.add(xyPlane)
    baseSketch.name = 'baseSketch'
    camSketch = sketches.add(xyPlane)
    camSketch.name = 'camSketch'
    diskCircles = diskSketch.sketchCurves.sketchCircles
    baseCircles = baseSketch.sketchCurves.sketchCircles
    camCircles = camSketch.sketchCurves.sketchCircles
    points = adsk.core.ObjectCollection.create()
    bodyCollection = adsk.core.ObjectCollection.create()

    # create the sketch for the cycloidal disk
    px = 0
    py = 0
    pz = 0
    for i in range(360):
        currentRad = i * math.pi / 180.0
        alpha = currentRad * fixedN
        # parametric equations to create a spline along the outer edge
        px = effectiveR * math.cos(currentRad) + (eccentricity * math.cos(alpha))
        py = effectiveR * math.sin(currentRad) + (eccentricity * math.sin(alpha))
        point = adsk.core.Point3D.create(px, py, pz)
        points.add(point)
        if (i == 0):
            point0 = point
    points.add(point0)
    spline = diskSketch.sketchCurves.sketchFittedSplines.add(points)
    curves = diskSketch.findConnectedCurves(diskSketch.sketchCurves.sketchFittedSplines.add(points))
    dirPoint = adsk.core.Point3D.create(0, 0, 0)
    offsetCurves = diskSketch.offset(curves, dirPoint, (fixedDp / 2.0))
    shaftHole = diskCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), shaftR)
    for i in range(outputN):
        angle = i * 2.0 * math.pi / outputN
        px = (outputD / 2.0) * math.cos(angle)
        py = (outputD / 2.0) * math.sin(angle)
        diskCircles.addByCenterRadius(adsk.core.Point3D.create(px, py, 0), outputDp)

    # extrude the disk
    prof = diskSketch.profiles.item(1)
    distance = adsk.core.ValueInput.createByReal(diskHeight)
    diskExtrude = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)        
    disk = diskExtrude.bodies.item(0)
    disk.name = "cycloidal disk"

    # create the sketch for the base
    baseCircle = baseCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), (fixedD / 2.0) + (fixedDp / 2.0) + 0.5)

    # extrude the base
    prof = baseSketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(-baseHeight)
    baseExtrude = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)    
    bodyCollection.add(baseExtrude.bodies.item(0))    

    # create the sketch for the center pin
    centerPin = baseCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), centerpinR)

    # extrude the center pin
    prof = baseSketch.profiles.item(1)
    distance = adsk.core.ValueInput.createByReal(pinHeight)
    baseExtrude2 = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)        
    base2 = baseExtrude2.bodies.item(0)

    # create the sketches for the outer pins
    degreeInc = (360.0 / fixedN) * (math.pi / 180.0)
    x = 0
    y = fixedD / 2.0
    z = 0
    count = 2
    for i in range(fixedN):
        baseCircles.addByCenterRadius(adsk.core.Point3D.create(x, y, z), fixedDp * 0.5)
        newy = x*math.sin(degreeInc) + y*math.cos(degreeInc)
        newx = x *math.cos(degreeInc) - y*math.sin(degreeInc)
        x = newx
        y = newy
        prof = baseSketch.profiles.item(count)
        distance = adsk.core.ValueInput.createByReal(pinHeight)
        baseExtrudes = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        count  = count + 1
        bodyCollection.add(baseExtrudes.bodies.item(0))  

    # combine the base components into one body
    combineFeatureInput = combineFeatures.createInput(base2, bodyCollection)
    combineFeatureInput.operation = 0
    combineFeatureInput.isKeepToolBodies = False
    combineFeatureInput.isNewComponent = False
    returnValue = combineFeatures.add(combineFeatureInput)
    returnValue.timelineObject.rollTo(True)       
    base = returnValue.targetBody
    base.name = "base"
    returnValue.timelineObject.rollTo(False)     
    
    # create the sketch for the cam, allowing for tolerances
    shaftHole = camCircles.addByCenterRadius(adsk.core.Point3D.create(0, 0, 0), shaftR - (tolerance))
    # pinD*0.5
    offsetPin = camCircles.addByCenterRadius(adsk.core.Point3D.create(0, eccentricity, 0), centerpinR + tolerance) 

    # extrude the cam
    prof = camSketch.profiles.item(0)
    distance = adsk.core.ValueInput.createByReal(camHeight)
    camExtrude = extrudes.addSimple(prof, distance, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)        
    cam = camExtrude.bodies.item(0)
    cam.name = "cam"
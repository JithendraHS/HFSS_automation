# ==========================================================
# 12-Layer Through Via Transition with BGA Ball
# HFSS Native IronPython Script
# ==========================================================
#
# Stackup:
#
# L1-L6  : 60 mil dielectric spacing
# L6-L7  : 200 mil dielectric spacing
# L7-L12 : 60 mil dielectric spacing
#
# Dk = 4
# Copper thickness = 1.4 mil
#
# Via:
# Drill = 13 mil
# Pad   = 25 mil
# Antipad = 45 mil
#
# BGA Ball:
# Height = 400 mil
#
# Units = mm
#
# ==========================================================

import ScriptEnv, math

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

oProject = oDesktop.NewProject()
oProject.InsertDesign(
    "HFSS",
    "Via_Transition_12Layer",
    "DrivenModal",
    ""
)

oDesign = oProject.SetActiveDesign("Via_Transition_12Layer")
oEditor = oDesign.SetActiveEditor("3D Modeler")

# ==========================================================
# PARAMETERS
# ==========================================================

MIL = 0.0254

CU_THICKNESS = 1.4 * MIL

DIEL_THIN = 60.0 * MIL
DIEL_MID  = 200.0 * MIL

DK = 4.0

DRILL_DIA   = 13.0 * MIL
PAD_DIA     = 25.0 * MIL
ANTIPAD_DIA = 45.0 * MIL

BALL_HEIGHT = 400.0 * MIL

BOARD_X = 20.0
BOARD_Y = 20.0

# ==========================================================
# BUILD STACKUP
# ==========================================================

layer_z = []

z = 0.0

for layer in range(12):

    layer_z.append(z)

    z += CU_THICKNESS

    if layer == 11:
        break

    if layer < 5:
        z += DIEL_THIN

    elif layer == 5:
        z += DIEL_MID

    else:
        z += DIEL_THIN

BOARD_THICKNESS = z

print "Board Thickness =", BOARD_THICKNESS

# ==========================================================
# CREATE DIELECTRIC BLOCK
# ==========================================================

oEditor.CreateBox(
[
"NAME:BoxParameters",
"XPosition:=","-10mm",
"YPosition:=","-10mm",
"ZPosition:=","0mm",
"XSize:=","20mm",
"YSize:=","20mm",
"ZSize:=",str(BOARD_THICKNESS)+"mm"
],
[
"NAME:Attributes",
"Name:=","Dielectric",
"Color:=","(132 200 255)",
"MaterialName:=","FR4_epoxy",
"SolveInside:=",True
])

# ==========================================================
# CREATE COPPER LAYERS
# ==========================================================

for i,z0 in enumerate(layer_z):

    oEditor.CreateBox(
    [
    "NAME:BoxParameters",
    "XPosition:=","-10mm",
    "YPosition:=","-10mm",
    "ZPosition:=",str(z0)+"mm",
    "XSize:=","20mm",
    "YSize:=","20mm",
    "ZSize:=",str(CU_THICKNESS)+"mm"
    ],
    [
    "NAME:Attributes",
    "Name:=","L"+str(i+1),
    "Color:=","(255 128 0)",
    "MaterialName:=","copper",
    "SolveInside:=",False
    ])

# ==========================================================
# CREATE VIA BARREL
# ==========================================================

oEditor.CreateCylinder(
[
"NAME:CylinderParameters",
"XCenter:=","0mm",
"YCenter:=","0mm",
"ZCenter:=","0mm",
"Radius:=",str(DRILL_DIA/2.0)+"mm",
"Height:=",str(BOARD_THICKNESS)+"mm",
"WhichAxis:=","Z"
],
[
"NAME:Attributes",
"Name:=","SignalVia",
"Color:=","(255 0 0)",
"MaterialName:=","copper",
"SolveInside:=",False
])

# ==========================================================
# CREATE PADS ON ALL LAYERS
# ==========================================================

for i,z0 in enumerate(layer_z):

    oEditor.CreateCylinder(
    [
    "NAME:CylinderParameters",
    "XCenter:=","0mm",
    "YCenter:=","0mm",
    "ZCenter:=",str(z0)+"mm",
    "Radius:=",str(PAD_DIA/2.0)+"mm",
    "Height:=",str(CU_THICKNESS)+"mm",
    "WhichAxis:=","Z"
    ],
    [
    "NAME:Attributes",
    "Name:=","Pad_L"+str(i+1),
    "Color:=","(255 255 0)",
    "MaterialName:=","copper",
    "SolveInside:=",False
    ])

# ==========================================================
# CREATE ANTIPADS
# ==========================================================

for i,z0 in enumerate(layer_z):

    oEditor.CreateCylinder(
    [
    "NAME:CylinderParameters",
    "XCenter:=","0mm",
    "YCenter:=","0mm",
    "ZCenter:=",str(z0-CU_THICKNESS)+"mm",
    "Radius:=",str(ANTIPAD_DIA/2.0)+"mm",
    "Height:=",str(CU_THICKNESS*3)+"mm",
    "WhichAxis:=","Z"
    ],
    [
    "NAME:Attributes",
    "Name:=","AntiPad_L"+str(i+1),
    "Color:=","(0 255 255)",
    "MaterialName:=","vacuum",
    "SolveInside:=",True
    ])

# ==========================================================
# SUBTRACT ANTIPADS FROM PLANES
# ==========================================================

for i in range(12):

    oEditor.Subtract(
    [
    "NAME:Selections",
    "Blank Parts:=","L"+str(i+1),
    "Tool Parts:=","AntiPad_L"+str(i+1)
    ],
    [
    "NAME:SubtractParameters",
    "KeepOriginals:=",False
    ])

# ==========================================================
# CREATE BGA BALL
# ==========================================================

BALL_RADIUS = PAD_DIA/2.0

oEditor.CreateSphere(
[
"NAME:SphereParameters",
"XCenter:=","0mm",
"YCenter:=","0mm",
"ZCenter:=",str(BOARD_THICKNESS+BALL_HEIGHT/2.0)+"mm",
"Radius:=",str(BALL_HEIGHT/2.0)+"mm"
],
[
"NAME:Attributes",
"Name:=","BGA_Ball",
"Color:=","(180 180 180)",
"MaterialName:=","solder",
"SolveInside:=",True
])

# ==========================================================
# UNION VIA + PADS
# ==========================================================

objects = ["SignalVia"]

for i in range(12):
    objects.append("Pad_L"+str(i+1))

oEditor.Unite(
[
"NAME:Selections",
"Selections:=",",".join(objects)
],
[
"NAME:UniteParameters",
"KeepOriginals:=",False
])

print "12-Layer Via Transition Generated"
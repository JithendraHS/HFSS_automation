# -*- coding: ascii -*-
"""
microstrip_hfss.py
==================
Ansys HFSS IronPython Script - Simple Microstrip, 2-Layer Stackup
------------------------------------------------------------------
Stackup (bottom to top):
  Layer 1 (bottom) : Ground plane (PEC sheet, zero thickness)
  Layer 2 (core)   : Dielectric,           height = 20 mil
  Layer 3 (top)    : Copper signal trace,  height = 1  mil

How to use inside HFSS:
    Tools --> Run Script --> select this file
"""

# ---------------------------------------------------------------------------
# PARAMETERS  (all dimensions in mil unless noted)
# ---------------------------------------------------------------------------
TRACE_LENGTH   = 500.0   # mil
TRACE_WIDTH    = 4.0     # mil
COPPER_HEIGHT  = 1.0     # mil
DIEL_HEIGHT    = 20.0    # mil
DIEL_ER        = 4.3
DIEL_LOSS_TAN  = 0.02

# Airbox padding
AIR_ABOVE  = 3.0 * DIEL_HEIGHT
AIR_SIDE   = 3.0 * DIEL_HEIGHT
AIR_BEYOND = 60.0

# Wave port PEC backing (internal ports)
PEC_CAP_THICKNESS = 1.0    # mil

# Frequency sweep
FREQ_START = "0.1GHz"
FREQ_STOP  = "10GHz"
FREQ_POINTS = 100

# Names
PROJECT_NAME = "Microstrip_2Layer"
DESIGN_NAME  = "Microstrip_Model"
SETUP_NAME   = "Setup1"
SWEEP_NAME   = "Sweep1"
UNITS        = "mil"

# ---------------------------------------------------------------------------
# DERIVED Z COORDINATES
# ---------------------------------------------------------------------------
z0 = 0.0                       # ground sheet (PEC)
z_diel_top = z0 + DIEL_HEIGHT  # top of dielectric / bottom of trace
z_trace_top = z_diel_top + COPPER_HEIGHT

PLANE_WIDTH = TRACE_WIDTH + 2.0 * (6.0 * TRACE_WIDTH)

x_air_min = 0.0          - AIR_BEYOND
x_air_max = TRACE_LENGTH + AIR_BEYOND
y_air_min = -(PLANE_WIDTH / 2.0) - AIR_SIDE
y_air_max =  (PLANE_WIDTH / 2.0) + AIR_SIDE
z_air_min = z0
z_air_max = z_trace_top + AIR_ABOVE

# ---------------------------------------------------------------------------
# HELPER
# ---------------------------------------------------------------------------
def m(val):
    return str(val) + UNITS

# ---------------------------------------------------------------------------
# BUILD
# ---------------------------------------------------------------------------
def build():

    # --- Project / Design ---------------------------------------------------
    oProject = oDesktop.NewProject()
    oProject.Rename(PROJECT_NAME + ".aedt", True)
    oProject.InsertDesign("HFSS", DESIGN_NAME, "HFSS Terminal Network", "")

    oDesign = oProject.SetActiveDesign(DESIGN_NAME)
    oEditor = oDesign.SetActiveEditor("3D Modeler")

    oEditor.SetModelUnits(
        ["NAME:Units Parameter", "Units:=", UNITS, "Rescale:=", False]
    )

    # --- Materials ----------------------------------------------------------
    # Use built-in "copper" for conductors -- avoids unit/SolveInside issues
    # Use a custom dielectric for the core

    oProjMgr = oProject.GetDefinitionManager()

    oProjMgr.AddMaterial(
        [
            "NAME:Core_Dielectric",
            "CoordinateSystemType:=",    "Cartesian",
            "BulkOrSurfaceType:=",       1,
            ["NAME:PhysicsTypes", "set:=", ["Electromagnetic"]],
            "permittivity:=",            str(DIEL_ER),
            "dielectric_loss_tangent:=", str(DIEL_LOSS_TAN),
        ]
    )

    # --- GND Plane (PEC sheet) ----------------------------------------------
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=",    m(0),
            "YStart:=",    m(-PLANE_WIDTH / 2.0),
            "ZStart:=",    m(z0),
            "Width:=",     m(TRACE_LENGTH),
            "Height:=",    m(PLANE_WIDTH),
            "WhichAxis:=", "Z",
        ],
        [
            "NAME:Attributes",
            "Name:=",          "GND_Plane",
            "Flags:=",         "",
            "Color:=",         "(255 128 0)",
            "Transparency:=",  0,
            "PartCoordinateSystem:=", "Global",
            "MaterialValue:=", "\"vacuum\"",
            "SolveInside:=",   True,
        ]
    )

    # --- Dielectric Core ----------------------------------------------------
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", m(0),
            "YPosition:=", m(-PLANE_WIDTH / 2.0),
            "ZPosition:=", m(z0),
            "XSize:=",     m(TRACE_LENGTH),
            "YSize:=",     m(PLANE_WIDTH),
            "ZSize:=",     m(DIEL_HEIGHT),
        ],
        [
            "NAME:Attributes",
            "Name:=",          "Core_Diel",
            "Flags:=",         "",
            "Color:=",         "(0 128 255)",
            "Transparency:=",  0.6,
            "PartCoordinateSystem:=", "Global",
            "MaterialValue:=", "\"Core_Dielectric\"",
            "SolveInside:=",   True,
        ]
    )

    # --- Signal Trace -------------------------------------------------------
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", m(0),
            "YPosition:=", m(-TRACE_WIDTH / 2.0),
            "ZPosition:=", m(z_diel_top),
            "XSize:=",     m(TRACE_LENGTH),
            "YSize:=",     m(TRACE_WIDTH),
            "ZSize:=",     m(COPPER_HEIGHT),
        ],
        [
            "NAME:Attributes",
            "Name:=",          "Signal_Trace",
            "Flags:=",         "",
            "Color:=",         "(255 165 0)",
            "Transparency:=",  0,
            "PartCoordinateSystem:=", "Global",
            "MaterialValue:=", "\"copper\"",
            "SolveInside:=",   False,
        ]
    )

    # --- Airbox -------------------------------------------------------------
    oEditor.CreateBox(
        [
            "NAME:BoxParameters",
            "XPosition:=", m(x_air_min),
            "YPosition:=", m(y_air_min),
            "ZPosition:=", m(z_air_min),
            "XSize:=",     m(x_air_max - x_air_min),
            "YSize:=",     m(y_air_max - y_air_min),
            "ZSize:=",     m(z_air_max - z_air_min),
        ],
        [
            "NAME:Attributes",
            "Name:=",          "Airbox",
            "Flags:=",         "",
            "Color:=",         "(128 255 255)",
            "Transparency:=",  0.8,
            "PartCoordinateSystem:=", "Global",
            "MaterialValue:=", "\"vacuum\"",
            "SolveInside:=",   True,
        ]
    )

    # --- Boundaries ---------------------------------------------------------
    oBound = oDesign.GetModule("BoundarySetup")

    oBound.AssignRadiation(
        [
            "NAME:Rad_Boundary",
            "Objects:=",        ["Airbox"],
            "IsFssReference:=", False,
            "IsForPML:=",       False,
        ]
    )

    oBound.AssignPerfectE(
        [
            "NAME:PerfE_GND",
            "Objects:=",        ["GND_Plane"],
            "InfGroundPlane:=", True,
        ]
    )

    # --- Wave Port 1 (x = 0, terminal solution) -----------------------------
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=",    m(0),
            "YStart:=",    m(y_air_min),
            "ZStart:=",    m(z_air_min),
            "Width:=",     m(y_air_max - y_air_min),
            "Height:=",    m(z_air_max - z_air_min),
            "WhichAxis:=", "X",
        ],
        [
            "NAME:Attributes",
            "Name:=",          "Port1_Face",
            "MaterialValue:=", "\"vacuum\"",
            "SolveInside:=",   True,
        ]
    )

    oBound.AssignWavePort(
        [
            "NAME:P1",
            "Objects:=",                 ["Port1_Face"],
            "NumModes:=",                1,
            "RenormalizeAllTerminals:=", True,
            "UseLineModeAlignment:=",    False,
            "DoDeembed:=",               False,
            "TerminalIDList:=",          [],
            "ShowReporterFilter:=",  False,
            "ReporterFilter:=",      [True],
            "UseAnalyticAlignment:=", False,
        ]
    )

    # --- Wave Port 2 (x = TRACE_LENGTH, terminal solution) ------------------
    oEditor.CreateRectangle(
        [
            "NAME:RectangleParameters",
            "IsCovered:=", True,
            "XStart:=",    m(TRACE_LENGTH),
            "YStart:=",    m(y_air_min),
            "ZStart:=",    m(z_air_min),
            "Width:=",     m(y_air_max - y_air_min),
            "Height:=",    m(z_air_max - z_air_min),
            "WhichAxis:=", "X",
        ],
        [
            "NAME:Attributes",
            "Name:=",          "Port2_Face",
            "MaterialValue:=", "\"vacuum\"",
            "SolveInside:=",   True,
        ]
    )

    oBound.AssignWavePort(
        [
            "NAME:P2",
            "Objects:=",                 ["Port2_Face"],
            "NumModes:=",                1,
            "RenormalizeAllTerminals:=", True,
            "UseLineModeAlignment:=",    False,
            "DoDeembed:=",               False,
            "TerminalIDList:=",          [],
            "ShowReporterFilter:=",  False,
            "ReporterFilter:=",      [True],
            "UseAnalyticAlignment:=", False,
        ]
    )

    # --- Terminals (signal trace vs GND reference) --------------------------
    _ref_cond = ["NAME:ReferenceConductors", "GND_Plane"]
    oBound.AutoIdentifyTerminals(_ref_cond, "P1", True)
    oBound.AutoIdentifyTerminals(_ref_cond, "P2", True)

    # --- PEC backing for internal wave ports --------------------------------
    z_port_mid = (z_air_min + z_air_max) / 2.0

    face_p1 = oEditor.GetFaceByPosition(
        [
            "NAME:FaceParameters",
            "BodyName:=", "Port1_Face",
            "XPosition:=", m(0),
            "YPosition:=", m(0),
            "ZPosition:=", m(z_port_mid),
        ]
    )
    oBound.AutoCreatePECCapForWavePort(
        [
            "NAME:AutoCreatePECCapForWavePort",
            "Wave Port Name:=", "P1",
            "Face ID:=",         face_p1,
            "Flip Side:=",       True,
            "Thickness:=",       m(PEC_CAP_THICKNESS),
        ]
    )

    face_p2 = oEditor.GetFaceByPosition(
        [
            "NAME:FaceParameters",
            "BodyName:=", "Port2_Face",
            "XPosition:=", m(TRACE_LENGTH),
            "YPosition:=", m(0),
            "ZPosition:=", m(z_port_mid),
        ]
    )
    oBound.AutoCreatePECCapForWavePort(
        [
            "NAME:AutoCreatePECCapForWavePort",
            "Wave Port Name:=", "P2",
            "Face ID:=",         face_p2,
            "Flip Side:=",       False,
            "Thickness:=",       m(PEC_CAP_THICKNESS),
        ]
    )

    # --- Solution Setup -----------------------------------------------------
    oAnalysis = oDesign.GetModule("AnalysisSetup")

    oAnalysis.InsertSetup(
        "HfssDriven",
        [
            "NAME:"             + SETUP_NAME,
            "AdaptMultipleFreqs:=", False,
            "Frequency:=",        FREQ_STOP,
            "MaxDeltaS:=",        0.02,
            "PortsOnly:=",        False,
            "UseMatrixConv:=",    False,
            "MaximumPasses:=",    10,
            "MinimumPasses:=",    2,
            "MinimumConvergedPasses:=", 1,
            "PercentRefinement:=", 30,
            "IsEnabled:=",        True,
            "BasisOrder:=",       1,
            "DoLambdaRefine:=",   True,
            "DoMaterialLambda:=",  True,
            "SetLambdaTarget:=",   False,
            "Target:=",            0.3333,
            "UseMaxTetIncrease:=", False,
            "PortAccuracy:=",      2,
            "UseABCOnPort:=",      False,
            "SetPortMinMaxTri:=",  False,
            "UseDomains:=",        True,
            "UseIterativeSolver:=", False,
            "SaveRadFieldsOnly:=", False,
            "SaveAnyFields:=",     True,
            "IESolverType:=",       "Auto",
            "LambdaTargetForIESolver:=", 0.15,
            "UseDefaultLambdaTgtForIESolver:=", True,
        ]
    )

    oAnalysis.InsertFrequencySweep(
        SETUP_NAME,
        [
            "NAME:"           + SWEEP_NAME,
            "IsEnabled:=",    True,
            "RangeType:=",    "LinearCount",
            "RangeStart:=",   FREQ_START,
            "RangeEnd:=",     FREQ_STOP,
            "RangeCount:=",   FREQ_POINTS,
            "Type:=",         "Interpolating",
            "SaveFields:=",   False,
            "SaveRadFields:=", False,
            "InterpTolerance:=", 0.5,
            "InterpMaxSolns:=",  250,
        ]
    )

    # --- Fit and save -------------------------------------------------------
    oEditor.FitAll()
    oProject.Save()

    AddWarningMessage("Microstrip build complete.")
    AddWarningMessage(
        "Stackup: PEC GND sheet / "
        + str(DIEL_HEIGHT) + "mil diel er=" + str(DIEL_ER)
        + " / " + str(COPPER_HEIGHT) + "mil Cu trace"
    )

# ---------------------------------------------------------------------------
# ENTRY POINT
# ---------------------------------------------------------------------------
build()
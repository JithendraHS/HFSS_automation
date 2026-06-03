# CPW Stripline with VSS Via Shielding - HFSS Native Script
# ==========================================================
# Compatible with HFSS built-in IronPython 2.7 script engine.
# Run via: Tools > Run Script
#
# Solution type : Driven Modal
# Topology      : Coplanar Waveguide (CPW) Stripline
#
# PARAMETRIC DESIGN - only edit Section 2 to change the model.
# All geometry is derived from these primary parameters:
#
#   TRACE_WIDTH   : width of the signal trace
#   CPW_GAP       : clearance between trace edge and coplanar ground
#   VIA_OFFSET    : distance from coplanar-ground inner edge to via centre
#
# The VSS via row automatically follows the inner edge of the
# coplanar ground on each side, so changing CPW_GAP or TRACE_WIDTH
# slides the entire via fence without any other edits needed.
#
# Stack-up (bottom to top):
#   Bottom ground  t=1.4mil  Z: -0.03556  to  0
#   Lower substrate h=60mil  Z:  0        to  1.524
#   CPW gnd + trace t=1.4mil Z:  1.524    to  1.55956
#   Upper substrate h=60mil  Z:  1.55956  to  3.08356
#   Top ground     t=1.4mil  Z:  3.08356  to  3.11912

import ScriptEnv, math

ScriptEnv.Initialize("Ansoft.ElectronicsDesktop")
oDesktop.RestoreWindow()

# ================================================================
# 2. PRIMARY PARAMETERS  -- edit here
# ================================================================

# --- Substrate / copper stack (all mm) --------------------------
SUB_WIDTH_MM       = 12.0      # Y extent of substrate
SUB_LENGTH_MM      = 20.0      # X extent (= trace length)
SUB_THICKNESS_MM   = 1.524     # 60 mil per dielectric layer
CU_THICKNESS_MM    = 0.03556   # 1.4 mil copper

# --- Signal trace -----------------------------------------------
TRACE_WIDTH_MM     = 2.54      # *** PRIMARY: 100 mil -- change freely ***

# --- CPW gap (trace edge to coplanar ground inner edge) ---------
CPW_GAP_MM         = 0.254     # *** PRIMARY: 10 mil  -- change freely ***

# --- Via placement ----------------------------------------------
# VIA_OFFSET_MM : distance from the coplanar-ground INNER edge
#                 (= from the gap/ground boundary) to the via CENTRE.
# Set to half the via diameter so the via just touches the inner edge.
VIA_DIAMETER_MM    = 0.508     # 20 mil
VIA_OFFSET_MM      = VIA_DIAMETER_MM / 2.0  # *** slides with CPW_GAP ***

VIA_PITCH_MM       = 1.016     # 40 mil, spacing along X
VIA_RADIUS_MM      = VIA_DIAMETER_MM / 2.0

# --- Solution ---------------------------------------------------
FREQ_SOLVE         = "20GHz"
FREQ_START         = "1GHz"
FREQ_STOP          = "40GHz"
FREQ_POINTS        = 401

# ================================================================
# 3. DERIVED GEOMETRY  -- computed from primary parameters above
# ================================================================

# --- Trace Y extents ---
TRACE_Y_MM         = (SUB_WIDTH_MM - TRACE_WIDTH_MM) / 2.0
TRACE_Y_END_MM     = TRACE_Y_MM + TRACE_WIDTH_MM
TRACE_CENTER_Y_MM  = TRACE_Y_MM + TRACE_WIDTH_MM / 2.0

# --- CPW gap extents ---
# Left  gap: TRACE_Y_MM - CPW_GAP_MM  to  TRACE_Y_MM
# Right gap: TRACE_Y_END_MM           to  TRACE_Y_END_MM + CPW_GAP_MM
CPW_GND_L_END_MM   = TRACE_Y_MM - CPW_GAP_MM          # inner edge of left  CPW gnd
CPW_GND_R_START_MM = TRACE_Y_END_MM + CPW_GAP_MM      # inner edge of right CPW gnd

CPW_GND_L_WIDTH_MM = CPW_GND_L_END_MM                 # from Y=0
CPW_GND_R_WIDTH_MM = SUB_WIDTH_MM - CPW_GND_R_START_MM

# --- Via centre Y ---
# Left  via: just inside the left  CPW ground inner edge  -> Y decreases from inner edge
# Right via: just inside the right CPW ground inner edge  -> Y increases from inner edge
VIA_L_Y_MM         = CPW_GND_L_END_MM  - VIA_OFFSET_MM
VIA_R_Y_MM         = CPW_GND_R_START_MM + VIA_OFFSET_MM

# --- Via count and first X position ---
VIA_FIRST_X_MM     = VIA_PITCH_MM / 2.0
VIA_COUNT          = int(math.floor((SUB_LENGTH_MM - VIA_FIRST_X_MM) / VIA_PITCH_MM)) + 1

# --- Z stack (fixed) ---
Z_BOT_GND_BOT_MM   = -CU_THICKNESS_MM          # -0.03556
Z_BOT_GND_TOP_MM   =  0.0
Z_TRACE_BOT_MM     =  SUB_THICKNESS_MM          #  1.524
Z_TRACE_TOP_MM     =  SUB_THICKNESS_MM + CU_THICKNESS_MM   #  1.55956
Z_TOP_SUB_TOP_MM   =  SUB_THICKNESS_MM + CU_THICKNESS_MM + SUB_THICKNESS_MM  # 3.08356
Z_TOP_GND_TOP_MM   =  Z_TOP_SUB_TOP_MM  + CU_THICKNESS_MM  # 3.11912

VIA_Z_BOT_MM       =  Z_BOT_GND_BOT_MM
VIA_HEIGHT_MM      =  Z_TOP_GND_TOP_MM - Z_BOT_GND_BOT_MM  # full stack

# --- Air box (0.5mm pad all sides) ---
AIR_PAD_MM         = 0.5
AIR_X_MM           = -AIR_PAD_MM
AIR_Y_MM           = -AIR_PAD_MM
AIR_Z_MM           =  Z_BOT_GND_BOT_MM - AIR_PAD_MM
AIR_XSIZE_MM       =  SUB_LENGTH_MM + 2.0 * AIR_PAD_MM
AIR_YSIZE_MM       =  SUB_WIDTH_MM  + 2.0 * AIR_PAD_MM
AIR_ZSIZE_MM       =  VIA_HEIGHT_MM + 2.0 * AIR_PAD_MM

# --- Port cross-section ---
PORT_Z_START_MM    =  Z_BOT_GND_BOT_MM
PORT_Z_HEIGHT_MM   =  Z_TOP_GND_TOP_MM - Z_BOT_GND_BOT_MM  # 3.15468

# Integration line from inner face of bottom gnd to inner face of top gnd
INTLINE_Z_START_MM =  0.0
INTLINE_Z_END_MM   =  Z_TOP_SUB_TOP_MM   # 3.08356

# ================================================================
# Helper: round float to 6 dp and append "mm"
# ================================================================
def mm(v):
    return str(round(v, 6)) + "mm"

# ================================================================
# 4. PRINT PARAMETER SUMMARY TO MESSAGE WINDOW
# ================================================================
print("=" * 52)
print("CPW Stripline parameters")
print("  TRACE_WIDTH   = " + mm(TRACE_WIDTH_MM))
print("  CPW_GAP       = " + mm(CPW_GAP_MM))
print("  TRACE_Y       = " + mm(TRACE_Y_MM))
print("  CPW gnd L end = " + mm(CPW_GND_L_END_MM))
print("  CPW gnd R start="+ mm(CPW_GND_R_START_MM))
print("  Via L Y       = " + mm(VIA_L_Y_MM))
print("  Via R Y       = " + mm(VIA_R_Y_MM))
print("  Via count/row = " + str(VIA_COUNT))
print("  Via first X   = " + mm(VIA_FIRST_X_MM))
print("=" * 52)

# ================================================================
# 5. CREATE PROJECT AND HFSS DESIGN
# ================================================================
oProject = oDesktop.NewProject()
oProject.Rename("CPW_Stripline_Project", True)
oProject.InsertDesign("HFSS", "CPW_Stripline", "DrivenModal", "")
oDesign = oProject.SetActiveDesign("CPW_Stripline")

oEditor      = oDesign.SetActiveEditor("3D Modeler")
oBoundary    = oDesign.GetModule("BoundarySetup")
oAnalysis    = oDesign.GetModule("AnalysisSetup")
oOptimetrics = oDesign.GetModule("Optimetrics")

# ================================================================
# 6. ADD CUSTOM MATERIAL
# ================================================================
oDefinitionManager = oProject.GetDefinitionManager()

oDefinitionManager.AddMaterial(
    [
        "NAME:Rogers_RO3003",
        "CoordinateSystemType:=",     "Cartesian",
        "BulkOrSurfaceType:=",        1,
        [
            "NAME:PhysicsTypes",
            "set:=", ["Electromagnetic"],
        ],
        "permittivity:=",             "3.2",
        "dielectric_loss_tangent:=",  "0.002",
    ]
)

# ================================================================
# 7. GEOMETRY
# ================================================================

# -- 7a. Bottom ground --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", "0mm",
        "ZPosition:=", mm(Z_BOT_GND_BOT_MM),
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(SUB_WIDTH_MM),
        "ZSize:=",     mm(CU_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "Ground_Bot",
        "Color:=",        "(255 128 65)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"copper\"",
        "SolveInside:=",  False,
    ]
)

# -- 7b. Lower substrate --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", "0mm",
        "ZPosition:=", "0mm",
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(SUB_WIDTH_MM),
        "ZSize:=",     mm(SUB_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "Substrate_Lower",
        "Color:=",        "(143 175 143)",
        "Transparency:=", 0.4,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"Rogers_RO3003\"",
        "SolveInside:=",  True,
    ]
)

# -- 7c. Signal trace --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", mm(TRACE_Y_MM),
        "ZPosition:=", mm(Z_TRACE_BOT_MM),
        "XSize:=",     mm(TRACE_WIDTH_MM),
        "YSize:=",     mm(TRACE_WIDTH_MM),
        "ZSize:=",     mm(CU_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "Trace",
        "Color:=",        "(255 215 0)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"copper\"",
        "SolveInside:=",  False,
    ]
)

# Corrected trace: XSize should be the trace length not width
oEditor.Delete(["NAME:Selections", "Selections:=", "Trace"])
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", mm(TRACE_Y_MM),
        "ZPosition:=", mm(Z_TRACE_BOT_MM),
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(TRACE_WIDTH_MM),
        "ZSize:=",     mm(CU_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "Trace",
        "Color:=",        "(255 215 0)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"copper\"",
        "SolveInside:=",  False,
    ]
)

# -- 7d. Coplanar ground LEFT --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", "0mm",
        "ZPosition:=", mm(Z_TRACE_BOT_MM),
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(CPW_GND_L_WIDTH_MM),
        "ZSize:=",     mm(CU_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "CPW_Gnd_Left",
        "Color:=",        "(255 128 65)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"copper\"",
        "SolveInside:=",  False,
    ]
)

# -- 7e. Coplanar ground RIGHT --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", mm(CPW_GND_R_START_MM),
        "ZPosition:=", mm(Z_TRACE_BOT_MM),
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(CPW_GND_R_WIDTH_MM),
        "ZSize:=",     mm(CU_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "CPW_Gnd_Right",
        "Color:=",        "(255 128 65)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"copper\"",
        "SolveInside:=",  False,
    ]
)

# -- 7f. Upper substrate --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", "0mm",
        "ZPosition:=", mm(Z_TRACE_TOP_MM),
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(SUB_WIDTH_MM),
        "ZSize:=",     mm(SUB_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "Substrate_Upper",
        "Color:=",        "(143 175 143)",
        "Transparency:=", 0.4,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"Rogers_RO3003\"",
        "SolveInside:=",  True,
    ]
)

# -- 7g. Top ground --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", "0mm",
        "YPosition:=", "0mm",
        "ZPosition:=", mm(Z_TOP_SUB_TOP_MM),
        "XSize:=",     mm(SUB_LENGTH_MM),
        "YSize:=",     mm(SUB_WIDTH_MM),
        "ZSize:=",     mm(CU_THICKNESS_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "Ground_Top",
        "Color:=",        "(255 128 65)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"copper\"",
        "SolveInside:=",  False,
    ]
)

# -- 7h. VSS Via fence --
# Via centre Y slides with CPW_GAP: sits VIA_OFFSET from the
# inner edge of the coplanar ground (touching the gap boundary).
via_objects = []
for i in range(VIA_COUNT):
    x_mm = VIA_FIRST_X_MM + i * VIA_PITCH_MM
    x_str = mm(x_mm)

    name_l = "Via_L_" + str(i + 1)
    name_r = "Via_R_" + str(i + 1)

    oEditor.CreateCylinder(
        [
            "NAME:CylinderParameters",
            "XCenter:=", x_str,
            "YCenter:=", mm(VIA_L_Y_MM),
            "ZCenter:=", mm(VIA_Z_BOT_MM),
            "Radius:=",  mm(VIA_RADIUS_MM),
            "Height:=",  mm(VIA_HEIGHT_MM),
            "WhichAxis:=", "Z",
            "NumSides:=",  0,
        ],
        [
            "NAME:Attributes",
            "Name:=",         name_l,
            "Color:=",        "(200 100 0)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "MaterialValue:=", "\"copper\"",
            "SolveInside:=",  False,
        ]
    )

    oEditor.CreateCylinder(
        [
            "NAME:CylinderParameters",
            "XCenter:=", x_str,
            "YCenter:=", mm(VIA_R_Y_MM),
            "ZCenter:=", mm(VIA_Z_BOT_MM),
            "Radius:=",  mm(VIA_RADIUS_MM),
            "Height:=",  mm(VIA_HEIGHT_MM),
            "WhichAxis:=", "Z",
            "NumSides:=",  0,
        ],
        [
            "NAME:Attributes",
            "Name:=",         name_r,
            "Color:=",        "(200 100 0)",
            "Transparency:=", 0,
            "PartCoordinateSystem:=", "Global",
            "MaterialValue:=", "\"copper\"",
            "SolveInside:=",  False,
        ]
    )

    via_objects.append(name_l)
    via_objects.append(name_r)

# -- 7i. Air box --
oEditor.CreateBox(
    [
        "NAME:BoxParameters",
        "XPosition:=", mm(AIR_X_MM),
        "YPosition:=", mm(AIR_Y_MM),
        "ZPosition:=", mm(AIR_Z_MM),
        "XSize:=",     mm(AIR_XSIZE_MM),
        "YSize:=",     mm(AIR_YSIZE_MM),
        "ZSize:=",     mm(AIR_ZSIZE_MM),
    ],
    [
        "NAME:Attributes",
        "Name:=",         "AirBox",
        "Color:=",        "(128 255 255)",
        "Transparency:=", 0.8,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"air\"",
        "SolveInside:=",  True,
    ]
)

# ================================================================
# 8. BOUNDARIES
# ================================================================

oBoundary.AssignRadiation(
    [
        "NAME:Rad1",
        "Objects:=",        ["AirBox"],
        "IsFssReference:=", False,
        "IsForPML:=",       False,
    ]
)

oBoundary.AssignPerfectE(
    ["NAME:PerfE_Ground_Bot",  "Objects:=", ["Ground_Bot"],     "InfGroundPlane:=", False]
)
oBoundary.AssignPerfectE(
    ["NAME:PerfE_Ground_Top",  "Objects:=", ["Ground_Top"],     "InfGroundPlane:=", False]
)
oBoundary.AssignPerfectE(
    ["NAME:PerfE_Trace",       "Objects:=", ["Trace"],          "InfGroundPlane:=", False]
)
oBoundary.AssignPerfectE(
    ["NAME:PerfE_CPW_Gnd_L",   "Objects:=", ["CPW_Gnd_Left"],   "InfGroundPlane:=", False]
)
oBoundary.AssignPerfectE(
    ["NAME:PerfE_CPW_Gnd_R",   "Objects:=", ["CPW_Gnd_Right"],  "InfGroundPlane:=", False]
)
oBoundary.AssignPerfectE(
    ["NAME:PerfE_Vias",        "Objects:=", via_objects,        "InfGroundPlane:=", False]
)

# ================================================================
# 9. WAVE PORTS
# ================================================================

PORT_Z_START  = mm(PORT_Z_START_MM)
PORT_Z_HEIGHT = mm(PORT_Z_HEIGHT_MM)

# Port 1  (at x=0)
oEditor.CreateRectangle(
    [
        "NAME:RectParameters",
        "IsCovered:=", True,
        "XStart:=",    "0mm",
        "YStart:=",    "0mm",
        "ZStart:=",    PORT_Z_START,
        "Width:=",     mm(SUB_WIDTH_MM),
        "Height:=",    PORT_Z_HEIGHT,
        "WhichAxis:=", "X",
    ],
    [
        "NAME:Attributes",
        "Name:=",      "Port1_Rect",
        "Color:=",     "(0 0 255)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"vacuum\"",
        "SolveInside:=", True,
    ]
)

oBoundary.AssignWavePort(
    [
        "NAME:Port1",
        "Objects:=",                 ["Port1_Rect"],
        "NumModes:=",                1,
        "RenormalizeAllTerminals:=", True,
        "UseLineModeAlignment:=",    False,
        "DoDeembed:=",               False,
        [
            "NAME:Modes",
            [
                "NAME:Mode1",
                "ModeNum:=",    1,
                "UseIntLine:=", True,
                [
                    "NAME:IntLine",
                    "Start:=", ["0mm", mm(TRACE_CENTER_Y_MM), mm(INTLINE_Z_START_MM)],
                    "End:=",   ["0mm", mm(TRACE_CENTER_Y_MM), mm(INTLINE_Z_END_MM)],
                ],
                "CharImp:=", "Zpi",
            ],
        ],
        "ShowReporterFilter:=",   False,
        "ReporterFilter:=",       [True],
        "UseAnalyticAlignment:=", False,
    ]
)

# Port 2  (at x=SUB_LENGTH)
oEditor.CreateRectangle(
    [
        "NAME:RectParameters",
        "IsCovered:=", True,
        "XStart:=",    mm(SUB_LENGTH_MM),
        "YStart:=",    "0mm",
        "ZStart:=",    PORT_Z_START,
        "Width:=",     mm(SUB_WIDTH_MM),
        "Height:=",    PORT_Z_HEIGHT,
        "WhichAxis:=", "X",
    ],
    [
        "NAME:Attributes",
        "Name:=",      "Port2_Rect",
        "Color:=",     "(0 0 255)",
        "Transparency:=", 0,
        "PartCoordinateSystem:=", "Global",
        "MaterialValue:=", "\"vacuum\"",
        "SolveInside:=", True,
    ]
)

oBoundary.AssignWavePort(
    [
        "NAME:Port2",
        "Objects:=",                 ["Port2_Rect"],
        "NumModes:=",                1,
        "RenormalizeAllTerminals:=", True,
        "UseLineModeAlignment:=",    False,
        "DoDeembed:=",               False,
        [
            "NAME:Modes",
            [
                "NAME:Mode1",
                "ModeNum:=",    1,
                "UseIntLine:=", True,
                [
                    "NAME:IntLine",
                    "Start:=", [mm(SUB_LENGTH_MM), mm(TRACE_CENTER_Y_MM), mm(INTLINE_Z_START_MM)],
                    "End:=",   [mm(SUB_LENGTH_MM), mm(TRACE_CENTER_Y_MM), mm(INTLINE_Z_END_MM)],
                ],
                "CharImp:=", "Zpi",
            ],
        ],
        "ShowReporterFilter:=",   False,
        "ReporterFilter:=",       [True],
        "UseAnalyticAlignment:=", False,
    ]
)

# ================================================================
# 10. SOLUTION SETUP + SWEEP
# ================================================================
oAnalysis.InsertSetup(
    "HfssDriven",
    [
        "NAME:Setup1",
        "Frequency:=",                FREQ_SOLVE,
        "MaxDeltaS:=",                0.02,
        "MaximumPasses:=",            20,
        "MinimumPasses:=",            2,
        "MinimumConvergedPasses:=",   2,
        "PercentRefinement:=",        30,
        "IsEnabled:=",                True,
        "BasisOrder:=",               1,
        "DoLambdaRefine:=",           True,
        "DoMaterialLambda:=",         True,
        "SetLambdaTarget:=",          False,
        "Target:=",                   0.3333,
        "UseMaxTetIncrease:=",        False,
        "PortAccuracy:=",             2,
        "UseABCOnPort:=",             False,
        "SetPortMinMaxTri:=",         False,
        "UseDomains:=",               False,
        "UseIterativeSolver:=",       False,
        "SaveRadFieldsOnly:=",        False,
        "SaveAnyFields:=",            True,
    ]
)

oAnalysis.InsertFrequencySweep(
    "Setup1",
    [
        "NAME:Sweep1",
        "IsEnabled:=",            True,
        "RangeType:=",            "LinearCount",
        "RangeStart:=",           FREQ_START,
        "RangeEnd:=",             FREQ_STOP,
        "RangeCount:=",           FREQ_POINTS,
        "Type:=",                 "Interpolating",
        "SaveFields:=",           False,
        "SaveRadFields:=",        False,
        "InterpTolerance:=",      0.5,
        "InterpMaxSolns:=",       250,
        "InterpMinSolns:=",       0,
        "InterpMinSubranges:=",   1,
        "ExtrapToDC:=",           False,
        "InterpUseS:=",           True,
        "InterpUsePortImped:=",   False,
        "InterpUsePropConst:=",   True,
        "UseDerivativeConvergence:=", False,
        "InterpDerivTolerance:=", 0.2,
        "UseFullBasis:=",         True,
        "EnforcePassivity:=",     True,
        "PassivityErrorTolerance:=", 0.0001,
    ]
)

# ================================================================
# 11. REGISTER HFSS DESIGN VARIABLES
# ================================================================
# Declare the three primary parameters as HFSS design variables so
# they appear in the Variables tab and can be referenced by Optimetrics.

oDesign.ChangeProperty(
    [
        "NAME:AllTabs",
        [
            "NAME:LocalVariableTab",
            [
                "NAME:PropServers",
                "LocalVariables",
            ],
            [
                "NAME:NewProps",
                [
                    "NAME:TRACE_WIDTH",
                    "PropType:=",   "VariableProp",
                    "UserDef:=",    True,
                    "Value:=",      mm(TRACE_WIDTH_MM),
                ],
                [
                    "NAME:CPW_GAP",
                    "PropType:=",   "VariableProp",
                    "UserDef:=",    True,
                    "Value:=",      mm(CPW_GAP_MM),
                ],
                [
                    "NAME:VIA_DIAMETER",
                    "PropType:=",   "VariableProp",
                    "UserDef:=",    True,
                    "Value:=",      mm(VIA_DIAMETER_MM),
                ],
            ],
        ],
    ]
)

# ================================================================
# 12. OPTIMETRICS PARAMETRIC SWEEP
# ================================================================
# Adds a parametric sweep under Optimetrics that sweeps all three
# primary variables independently. Each variable gets its own
# linear step range centred on the nominal value.
#
# Sweep ranges (edit as needed):
#   TRACE_WIDTH : 1.524mm to 3.556mm  step 0.508mm  (60->140 mil, step 20 mil)
#   CPW_GAP     : 0.127mm to 0.508mm  step 0.127mm  (5->20 mil,   step 5 mil)
#   VIA_DIAMETER: 0.254mm to 0.762mm  step 0.254mm  (10->30 mil,  step 10 mil)

oOptimetrics.AddSetup(
    "OptiParametric",
    [
        "NAME:ParamSweep1",
        "IsEnabled:=",       True,
        "ProdOptiSetupDataV2:=", [
            "NAME:ProdOptiSetupDataV2",
            "SaveFields:=",  False,
            "CopyMesh:=",    False,
            "FastSweep:=",   False,
        ],
        "ProdOptiSolution:=", [
            "NAME:ProdOptiSolution",
            "OptimizationSetup:=", "Setup1 : Sweep1",
        ],
        [
            "NAME:Sweeps",
            [
                "NAME:SweepDefinition",
                "Variable:=",   "TRACE_WIDTH",
                "Data:=",       "LIN 1.524mm 3.556mm 0.508mm",
                "OffsetF1:=",   False,
                "Synchronize:=", 0,
            ],
            [
                "NAME:SweepDefinition",
                "Variable:=",   "CPW_GAP",
                "Data:=",       "LIN 0.127mm 0.508mm 0.127mm",
                "OffsetF1:=",   False,
                "Synchronize:=", 0,
            ],
            [
                "NAME:SweepDefinition",
                "Variable:=",   "VIA_DIAMETER",
                "Data:=",       "LIN 0.254mm 0.762mm 0.254mm",
                "OffsetF1:=",   False,
                "Synchronize:=", 0,
            ],
        ],
        "Sweep Operations:=", "Combinations",
        "Goals:=", [],
    ]
)

# ================================================================
# 13. SAVE
# ================================================================
oProject.Save()

oDesktop.AddMessage(
    "CPW_Stripline_Project",
    "CPW_Stripline",
    0,
    "CPW Stripline created. " +
    "W=" + mm(TRACE_WIDTH_MM) +
    " gap=" + mm(CPW_GAP_MM) +
    " Via_L_Y=" + mm(VIA_L_Y_MM) +
    " Via_R_Y=" + mm(VIA_R_Y_MM) +
    " vias/row=" + str(VIA_COUNT)
)

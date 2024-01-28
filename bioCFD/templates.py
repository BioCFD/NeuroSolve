'''
Number of help strings to be used as String.Templates
'''

TRI_SUR = '''
    ${stl_name}
    {
        type            triSurfaceMesh;
        name            ${patch_name};
    }
'''

BOX = '''
    ${name}
    {
        type            searchableBox;
        min             ${min_pt};
        max             ${max_pt};
    }
'''

EDGES='''
    {
        file ${emesh};
        level ${levels};
    }
'''

REF_SUR='''
    ${patch_name}
    {
        level (${min_level} ${max_level});
        patchInfo { type patch; }
    }
'''
LAYERS='''
    {
        nSurfaceLayers ${nlayers};
    }
'''
PHI_SOL='''
    {
        solver          GAMG;
        smoother        GaussSeidel;
        tolerance       1e-6;
        relTol          0.1;
    }
'''

INLET_U='''
    {
        type            flowRateInletVelocity;
        value           $internalField;
        volumetricFlowRate     csvFile;
        nHeaderLine     1;
        refColumn       0;
        componentColumns ( 1 );
        separator       ",";
        mergeSeparators no;
        file            "${FILE_NAME}";
        outOfBounds         repeat;      // optional out-of-bounds handling
        interpolationScheme linear;     // optional interpolation scheme       
    }
'''
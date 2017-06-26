"""Basic SSWind WPS implemenation."""
from pywps import EO4AProcess  # Import the EO4AProcess class
from pywps import ComplexInput, LiteralInput, LiteralOutput
from pywps.inout.literaltypes import AllowedValue
from pywps.validator.allowed_value import ALLOWEDVALUETYPE
from pywps import UOM
import os
import glob

# WPS Format validation
from pywps import Format
from pywps.validator.mode import MODE
from pywps.app.Common import Metadata

__author__ = 'ajuracic'


class CreateTiff(EO4AProcess):
    """Create GeoTiff from netcdf file, by starting with Sentinel 1 zip.

    Parameters
    ----------
    zipdir : input Sentinel zip file

    Returns
    ----------
    output_dir: The path to the GeoTiff file
    """

    def __init__(self):
        """Inputs and outputs for run_nc2tiff.sh sript."""
        inputs = [
            LiteralInput(
                'zipdir', 'input zip path',
                abstract="""
                Input Sentinel 1 zip file path.
                """,
                data_type='string',
                min_occurs=1
            )
        ]
        outputs = [
            LiteralOutput(
                'output_dir',
                'Workflow data volume path',
                data_type='string',
                abstract="""
                Path to the output png file.
                """,
            )
        ]

        super(CreateTiff, self).__init__(
            identifier=os.path.basename(os.path.dirname(__file__)),
            abstract="""
            Sample GeoTiff generation service.
            """,
            version='0.1',
            title="SSWind Sample Service: GeoTiff creation",
            profile='',
            metadata=[Metadata('Testing')],
            inputs=inputs,
            outputs=outputs,
        )

    
    def get_command(self, request, response):
        """The service command. Do not do any processing here."""
        inputs = request.inputs
        #self.outdir = os.path.join(self.output_dir, "TiffExample")
        #self.mkdir_p(self.outdir)
        self.outdir = '/data_service/'
        return [
            "bash", "-x", "run_nc2tiff.sh", str(inputs['zipdir'][0].source), str(self.outdir)
        ]

    def set_output(self, request, response):
        """ Set the output path for the png file."""
        workflow_disk_result_path = self.get_workflow_disk_path(self.outdir)
        response.outputs['output_dir'].data = workflow_disk_result_path
        response.outputs['output_dir'].uom = UOM('unity')

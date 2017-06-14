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

__author__ = 'ajuracic'


class CreateTiff(EO4AProcess):
    """Create GeoTiff from netcdf file, by starting with Sentinel 1 zip.

    Parameters
    ----------
    zipfile : input Sentinel zip file

    Returns
    ----------
    output_dir: The path to the GeoTiff file
    """

    def __init__(self):
        """Inputs and outputs for run_nc2tiff.sh sript."""
        inputs = [
            LiteralInput(
                'zipfile', 'input zip file',
                abstract="""
                Input Sentinel 1 zip file.
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
            #'eo4a-sswind',
            abstract="""
            Sample GeoTiff generation service.
            """,
            version='0.1',
            title="SSWind Sample Service: GeoTiff creation",
            profile='',
            inputs=inputs,
            outputs=outputs,
        )

    
    def get_command(self, request, response):
        """The service command. Do not do any processing here."""
        inputs = request.inputs
        self.outdir = os.path.join(self.output_dir, "TiffExample")
        self.mkdir_p(self.outdir)
        return [
            "bash", "-x", "run_nc2tiff.sh", str(inputs['zipfile'][0].source), str(self.outdir)
        ]

    def set_output(self, request, response):
        """ Set the output path for the png file."""
        # We use get_workflow_disk_path to get the path that other services
        # can read from. /data_service is local to each service, but a read-
        # only version exists in the workflow directory
        workflow_disk_result_path = self.get_workflow_disk_path(
            self.outdir
        )
        response.outputs['output_dir'].data = workflow_disk_result_path
        response.outputs['output_dir'].uom = UOM('unity')

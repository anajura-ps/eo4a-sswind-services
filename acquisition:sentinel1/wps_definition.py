"""Basic sentinelsat WPS implemenation."""
from pywps import EO4AProcess  # Import the EO4AProcess class
from pywps import ComplexInput, LiteralInput, LiteralOutput
from pywps.inout.literaltypes import AllowedValue
from pywps.validator.allowed_value import ALLOWEDVALUETYPE
from pywps import UOM
import os

# WPS Format validation
from pywps import Format
from pywps.validator.mode import MODE
from pywps.app.Common import Metadata

__author__ = 'ajuracic'


class SentinelDownload(EO4AProcess):
    """Basic SentinelSat download of Sentinel 1 WPS service.

    Parameters
    ----------
    search_polygon: GeoJson region
    start_date: Start date YYYYMMDD
    end_date: End date YYYYMMDD

    Returns
    ----------
    output_dir: The path to the downloaded sentinel products
    """

    def __init__(self):
        """Sample."""
        inputs = [
            ComplexInput(
                'search_polygon', 'GeoJSON region',
                supported_formats=[Format('application/vnd.geo+json')],
                abstract="""
                GeoJson of region to search
                """,
                mode=MODE.SIMPLE,
                max_occurs=1
            ),
            LiteralInput(
                'start_date', 'Start date',
                abstract="""
                Datestamp in format YYYYMMDD
                """,
                data_type='integer',
                max_occurs=1
            ),
            LiteralInput(
                'end_date', 'End date',
                abstract="""
                Datestamp in format YYYYMMDD
                """,
                data_type='integer',
                max_occurs=1
            )
        ]
        outputs = [
            LiteralOutput(
                'output_dir',
                'Workflow data volume path',
                data_type='string',
                abstract="""
                Path to a directory within the Workflow Data volume.
                The service will store all outputs in this dir, then
                provide a reference to the directory which other services
                can use.
                """,
            )
        ]

        super(SentinelDownload, self).__init__(
            identifier='acquisition:sentinel1',
            abstract="""
            Use sentinelsat python module to download Sentinel 1 data
            """,
            version='0.1',
            title="Download Sentinel 1 Data (referencing data volume)",
            metadata=[Metadata('Testing')],
            profile='',
            inputs=inputs,
            outputs=outputs,
        )

    def get_command(self, request, response):
        """The service command. Do not do any processing here."""
        inputs = request.inputs
        self.sen1_dir = '/data_service/'
        #self.mkdir(self.sen1_dir)
        # Query, include only L2, OCN data
        self.query = "producttype=OCN"
        return [
            "sentinel", "search", "--sentinel1", "-d",
            "-s", str(inputs['start_date'][0].source),
            "-e", str(inputs['end_date'][0].source),
            "-q", str(self.query),
            "-p", str(self.sen1_dir),
            "ajuracic", "S1lj0M1k1!",
            inputs['search_polygon'][0].file
        ]

    def set_output(self, request, response):
        """Set the output from the WPS request."""
        workflow_disk_result_path = self.get_workflow_disk_path(self.sen1_dir)
        response.outputs['output_dir'].data = workflow_disk_result_path
        response.outputs['output_dir'].uom = UOM('unity')

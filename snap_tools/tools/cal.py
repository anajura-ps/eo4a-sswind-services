"""
SNAP Calibration tool.
"""
import logging

from pywps import LiteralInput, LiteralOutput  # Import supported WPS IO
from pywps import UOM

from utils.wps import EoToolProcess

__author__ = "Ana Juracic"

logger = logging.getLogger('PYWPS')

class Cal(EoToolProcess):
    """
    SNAP Calibration tool.
    """

    def __init__(self):
        inputs = [
            LiteralInput(
                'srcfile',
                'Source file name',
                data_type='string',
                abstract="""
                Full path to source file name.
                """,
                min_occurs=1,
                max_occurs=1,
            ),
            LiteralInput(
                'dstfile',
                'Destination file name',
                data_type='string',
                abstract="""
                Full path to destination file name.
                """,
                min_occurs=1,
                max_occurs=1,
            )
        ]
        outputs = [
            LiteralOutput(
                'dstfile',
                'Destination file name',
                data_type='string',
                abstract="""
                Full path to destination file name, generated by SNAP calibration.
                """,
            )
        ]

        super(Cal, self).__init__(
            identifier='cal',
            abstract="""
            Radiometric calibration of Sentinel-1 SAR data. 
            """,
            version='0.1',
            title="calibration",
            metadata=[Metadata('Preprocessing')],
            profile='',
            inputs=inputs,
            outputs=outputs,
        )


    def get_command(self, request, response):
        """The service command. Do not do any processing here."""
        logger.info('Request inputs: %s', request.inputs)

        return ['bash', '-c', '/opt/snap/bin/gpt Cal.xml -Psrcfile=%s -Pdstfile=%s' % (self._get_input(request, 'srcfile'),
                                                                                       self._get_input(request, 'dstfile'),
                                                        )
                ]


    def set_output(self, request, response):
        """Set the output from the WPS request."""
        # TODO: should the dstfile value be automatically generated?
        # For now, the user specifies it as an input.
        response.outputs['dstfile'].data = self._get_input(request, 'dstfile')
        response.outputs['dstfile'].uom = UOM('unity')
        
        
        

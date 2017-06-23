"""
WPS utilities
"""
import logging

from pywps import EO4AProcess  

__author__ = "Derek O'Callaghan"

logger = logging.getLogger('PYWPS')


class EoToolProcess(EO4AProcess):

    def _get_input(self, request, identifier):
        return request.inputs[identifier][0].source if identifier in request.inputs else ''
    
    
    def _boolean_input(self, request, identifier):
        return '-%s' % identifier if self._get_input(request, identifier) else ''


    def _optional_input(self, request, identifier):
        input_value = self._get_input(request, identifier)
        if input_value:
            input_value = '-%s %s' % (identifier, input_value)
        return input_value
        
        
    def _boolean_params(self):
        return set([x.identifier for x in self.inputs if x.data_type=='boolean'])
    
    
    def _optional_params(self):
        return [x.identifier for x in self.inputs if x.identifier not in self._boolean_params() and x.min_occurs==0]
        
        
    def _boolean_params_str(self, request):
        return ' '.join([self._boolean_input(request, x) for x in self._boolean_params()])
    
    
    def _optional_params_str(self, request):
        return ' '.join([self._optional_input(request, x) for x in self._optional_params()])
    

        
        

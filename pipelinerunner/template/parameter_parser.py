from typing import List

from pipelinerunner.template.parameter_model import (
    TemplateParameter,
    TemplateParameterRequired,
    TemplateParameterType
)

# TO DO
# Ainda não estou usando esse cara, usar quando for criar um template via CLI sem o modo interativo
class TemplateParameterParser:
    @staticmethod
    def parse(parameters: str) -> List[TemplateParameter]:
        """
            Receiving the input in the format has shown in the following example
                AGENT_ENVIRONMENT:string:required:default=dev:options=dev,stg,prd
        """
        parts = parameters.split(':')
    
        if len(parts) < 3:
            raise ValueError(
                f"Invalid parameter format: {parameters}\n"
                "Expected: name:type:required[:default=VALUE][:options=VAL1,VAL2]"
            )
        
        name = parts[0]
        type = parts[1]
        required_flag = parts[2]
        
        if type not in TemplateParameterType.values():
            raise ValueError(f"Invalid type '{type}'. Must be: {TemplateParameterType.values()}")
        
        if required_flag not in TemplateParameterRequired.values():
            raise ValueError(f"Invalid required_flag '{required_flag}'. Must be: {TemplateParameterRequired.values()}")
        
        template_parameter = TemplateParameter(
            name = name,
            type = type,
            required = required_flag
        )

        # Parse optional parts
        for part in parts[3:]:
            if part.startswith('default='):
                template_parameter.default_value = part.split('=', 1)[1]
            elif part.startswith('options='):
                options_str = part.split('=', 1)[1]
                template_parameter.options = [ opt.strip() for opt in options_str.split(',') ]
        
        return template_parameter

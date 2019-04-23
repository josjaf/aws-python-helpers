import pathlib
import glob
import cfn_flip
import pprint
import os
from newport_helpers import helpers
class CombineHelpers():
    def __init__(self, *args, **kwargs):
        return
    def generate_role_boundary_mapping(self):
        role_boundary_mapping = []
        print()
        #role_files = os.listdir(os.path.abspath('role'))
        #boundary_files = os.listdir(os.path.abspath('boundary'))
        role_files = glob.glob('role/*')
        boundary_files = glob.glob('boundary/*')
        for role_file in role_files:
            #print(f"Role File: {role_file}")
            role_file_prefix = (pathlib.Path(role_file).stem).lower()
            #print(f"Processing Role: {role_file_prefix}")
            for boundary_file in boundary_files:
                # role_file = role_file.lower()
                # boundary_file = boundary_file.lower()
                boundary_file_prefix = (pathlib.Path(boundary_file).stem).lower()
                if role_file_prefix in boundary_file_prefix:
                    #print(f"Matched: {role_file} to {boundary_file}")
                    results = {'RoleName': role_file_prefix, 'BoundaryPath': os.path.abspath(boundary_file), 'RolePath': os.path.abspath(role_file)}
                    role_boundary_mapping.append(results)
                    break


        #pprint.pprint(role_boundary_mapping)
        return role_boundary_mapping
    def get_stack_set_config(self, role_boundary_mapping):
        Helpers = helpers.Helpers()
        Helpers.print_separator("Generating Role and Boundary Mapping")

        print(role_boundary_mapping)
        Helpers.print_separator("Combining Templates")
        stack_sets = []
        for combo in role_boundary_mapping:
            Helpers.print_separator(f"Processing Role: {combo['RoleName']}")
            #print(combo)

            boundary_body = Helpers.file_to_string(combo['BoundaryPath'])
            boundary_body_loaded = cfn_flip.load_yaml(boundary_body)
            role_body = Helpers.file_to_string(combo['RolePath'])
            role_body_loaded = cfn_flip.load_yaml(role_body)
            #import pdb; pdb.set_trace()
            final = role_body_loaded
            count = 0
            for resource in boundary_body_loaded['Resources']:
                if 'Boundary'.lower() in resource.lower():

                    count += 1

                    print(resource)
                    try:
                        final['Resources'][resource] = boundary_body_loaded['Resources'][resource]


                    except TypeError:
                        print(f"Got blank role template")
                        break
                    #clean_yaml = cfn_flip.to_yaml(final, clean_up=True)
                    #print(yaml.dump(final))
            result = {'TemplateBody': cfn_flip.dump_yaml(final), 
            'StackSetName': f"newport-{combo['RoleName']}", 
            'Description': f"{combo['RoleName']} Combined CFN from Newport Pipeline"
            }
            stack_sets.append(result)

        #print(stack_sets)
        if not stack_sets:
            raise RuntimeError(f"Stack Sets is empty, nothing to do. Check workdir")
        return stack_sets
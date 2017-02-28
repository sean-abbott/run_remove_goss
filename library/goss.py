#!/usr/bin/env python

import os
from ansible.module_utils.basic import *

DOCUMENTATION = '''
---
module: goss
author: Mathieu Corbin
short_description: Launch goss (https://github.com/aelsabbahy/goss) test
description:
    - Launch goss test. Always changed = False if success.
options:
    path:
        required: true
        description:
            - Test file to validate. Must be on the remote machine.
    format:
        required: false
        description:
            - change the output goss format.
            - Goss format list : goss v --format => [documentation json junit nagios rspecish tap].
            - Default: rspecish
    output_file:
        required: false
        description:
            - save the result of the goss command in a file whose path is output_file
examples:
    - name: test goss file
      goss:
        path: "/path/to/file.yml"

    - name: test goss files
      goss:
        path: "{{ item }}"
        format: json
        output_file : /my/output/file-{{ item }}
      with_items: "{{ goss_files }}"
'''


# launch goss validate command on the file
def check(module, test_file_path, output_format, executable='goss'):

    output_format = 'rspecish' if not output_format else output_format

    return module.run_command("{0} -g {1} v --format {2}".format(executable, test_file_path, output_format))


# write goss result to output_file_path
def output_file(output_file_path, out):
    if output_file_path is not None:
        with open(output_file_path, 'w') as output_file:
            output_file.write(out)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            path=dict(required=True, type='str'),
            format=dict(required=False, type='str'),
            output_file=dict(required=False, type='str'),
            executable=dict(required=False, type='str', default='goss')
        ),
        supports_check_mode=False
    )

    test_file_path = module.params['path']  # test file path
    output_format = module.params['format']  # goss output format
    output_file_path = module.params['output_file']
    executable = module.params['executable']

    if test_file_path is None:
        module.fail_json(msg="test file path is null")

    test_file_path = os.path.expanduser(test_file_path)

    # test if access to test file is ok

    if not os.access(test_file_path, os.R_OK):
        module.fail_json(msg="Test file %s not readable" % (test_file_path))

    # test if test file is not a dir
    if os.path.isdir(test_file_path):
        module.fail_json(msg="Test file must be a file ! : %s" % (test_file_path))

    (rc, out, err) = check(module, test_file_path, output_format, executable)

    if output_file_path is not None:
        output_file_path = os.path.expanduser(output_file_path)
        # check if output_file is a file
        if output_file_path.endswith(os.sep):
            module.fail_json(msg="output_file must be a file. Actually :  %s "
                             % (output_file_path))

        output_dirname = os.path.dirname(output_file_path)

        # check if output directory exists
        if not os.path.exists(output_dirname):
            module.fail_json(msg="directory %s does not exists" % (output_dirname))

        # check if writable
        if not os.access(os.path.dirname(output_file_path), os.W_OK):
            module.fail_json(msg="Destination %s not writable" % (os.path.dirname(output_file_path)))
        # write goss result on the output file
        output_file(output_file_path, out)

    if rc is not None and rc != 0:
        error_msg = "Goss Tests Failed"
        module.fail_json(msg=error_msg, stderr=err, stdout=out)

    result = {}
    result['stdout'] = out
    result['changed'] = False

    module.exit_json(**result)

main()


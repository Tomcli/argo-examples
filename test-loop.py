#!/usr/bin/env python3
# Copyright 2019 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import kfp.dsl as dsl
from kfp.dsl import _for_loop


class Coder:
    def __init__(self, ):
        self._code_id = 0

    def get_code(self, ):
        self._code_id += 1
        return '{code:0{num_chars:}d}'.format(code=self._code_id, num_chars=_for_loop.LoopArguments.NUM_CODE_CHARS)


dsl.ParallelFor._get_unique_id_code = Coder().get_code


@dsl.pipeline(name='my-pipeline')
def pipeline():
    op0 = dsl.ContainerOp(
        name="my-out-cop0",
        image='python:alpine3.6',
        command=["sh", "-c"],
        arguments=['python -c "import json; import sys; json.dump([{\'a\': 1, \'b\': 2}, {\'a\': 10, \'b\': 20}], open(\'/tmp/out.json\', \'w\'))"'],
        file_outputs={'out': '/tmp/out.json'},
    )

    with dsl.ParallelFor(op0.output) as item:
        with dsl.Condition(item.a == '1'):
            op1 = dsl.ContainerOp(
                name="my-in-cop1",
                image="library/bash:4.4.23",
                command=["sh", "-c"],
                arguments=["echo do output op1 item.a: %s" % item.a],
            )
            op2 = dsl.ContainerOp(
                name="my-in-cop1",
                image="library/bash:4.4.23",
                command=["sh", "-c"],
                arguments=["echo do output op1 item.a: %s" % item.a],
            ).after(op1)

    op_out = dsl.ContainerOp(
        name="my-out-cop2",
        image="library/bash:4.4.23",
        command=["sh", "-c"],
        arguments=["echo do output op2, outp: %s" % op0.output],
    )


if __name__ == '__main__':
    import kfp.compiler as compiler
    compiler.Compiler().compile(pipeline, __file__ + '.yaml')

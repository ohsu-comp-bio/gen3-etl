"""A transformer for gen3 project,reads cases bcc, writes to DEFAULT_OUTPUT_DIR."""
import hashlib
import os
import json

from gen3_etl.utils.ioutils import reader

from defaults import DEFAULT_OUTPUT_DIR, DEFAULT_EXPERIMENT_CODE, DEFAULT_PROJECT_ID, default_parser, emitter, obscure_dates
from gen3_etl.utils.schema import generate, template


def transform(item_paths, output_dir, experiment_code, compresslevel=0):
    """Read bcc labkey json and writes gen3 json."""
    cases_emitter = emitter('case', output_dir=output_dir)
    for p in item_paths:
        source = os.path.splitext(os.path.basename(p))[0]
        for line in reader(p):
            sample_id = line.rstrip('\n')
            submitter_id = sample_id
            case = {'type': 'case', 'experiments': {'submitter_id': experiment_code}, 'submitter_id': submitter_id, 'project_id': DEFAULT_PROJECT_ID}
            cases_emitter.write(case)
    cases_emitter.close()


if __name__ == "__main__":
    item_paths = ['source/gdan-tmp/gdan-tmp-sample_ids.txt']
    args = default_parser(DEFAULT_OUTPUT_DIR, DEFAULT_EXPERIMENT_CODE, DEFAULT_PROJECT_ID).parse_args()

    transform(item_paths, output_dir=args.output_dir, experiment_code=args.experiment_code)

    p = os.path.join(args.output_dir, 'case.json')
    assert os.path.isfile(p), 'should have an output file {}'.format(p)
    print(p)

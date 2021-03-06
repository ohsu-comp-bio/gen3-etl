
"""A transformer for gen3 project,reads treatments bcc, writes to DEFAULT_OUTPUT_DIR."""
import hashlib
import os
import json

from gen3_etl.utils.ioutils import reader

from defaults import DEFAULT_OUTPUT_DIR, DEFAULT_EXPERIMENT_CODE, DEFAULT_PROJECT_ID, default_parser, emitter, default_treatment, missing_parent, save_missing_parents
from gen3_etl.utils.schema import generate, template

def transform_gen3(item_paths, output_dir, project_id, compresslevel=0):
    """Creates gen3.treatment, returns set of treatment_ids."""
    submitted_file_emitter = emitter('submitted_file', output_dir=output_dir)
    for item_path in item_paths:
        for line in reader(item_path):
            submitter_id = '{}-{}'.format(line['participantid'], line['document'])
            submitted_file = {
                'type': 'bcc_submitted_file',
                'cases': {'submitter_id': line['participantid'] },
                'submitter_id': submitter_id,
                'project_id': project_id }
            submitted_file.update(line)
            for k in [ "_labkeyurl_data_owner", "_labkeyurl_doctype_id", "_labkeyurl_document", "_labkeyurl_participantid", ]:
                del submitted_file[k]
            submitted_file_emitter.write(submitted_file)
    submitted_file_emitter.close()


if __name__ == "__main__":
    item_paths = ['source/bcc/documentstore.json', ]
    args = default_parser(DEFAULT_OUTPUT_DIR, DEFAULT_EXPERIMENT_CODE, DEFAULT_PROJECT_ID).parse_args()
    transform_gen3(item_paths, args.output_dir, args.project_id)

    if args.schema:

        def my_callback(schema):
            schema['category'] = 'bcc extention'
            schema['properties']['case'] = {'$ref': '_definitions.yaml#/to_one'}
            return schema

        item_paths = ['output/bcc/submitted_file.json', ]

        link = {'name':'cases', 'backref':'bcc_submitted_files', 'label':'extends', 'target_type':'case',  'multiplicity': 'many_to_one', 'required': False }
        schema_path = generate(item_paths,'bcc_submitted_file', output_dir='output/bcc', links=[link], callback=my_callback)
        assert os.path.isfile(schema_path), 'should have an schema file {}'.format(schema_path)
        print(schema_path)

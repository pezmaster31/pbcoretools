import logging
import sys

from pbcommand.cli import pbparser_runner
from pbcommand.models import get_gather_pbparser, FileTypes
from pbcommand.utils import setup_log

from pbcoretools.chunking.gather import run_main_gather_csv

log = logging.getLogger(__name__)


class Constants(object):
    TOOL_ID = "pbcoretools.tasks.gather_csv"
    CHUNK_KEY = "$chunk.csv_id"
    VERSION = "0.1.0"
    DRIVER = "python -m pbcoretools.tasks.gather_csv --resolved-tool-contract "
    OPT_CHUNK_KEY = 'pbcoretools.task_options.gather_csv_chunk_key'


def get_parser():
    p = get_gather_pbparser(Constants.TOOL_ID,
                            Constants.VERSION,
                            "Dev CSV Gather",
                            "General Chunk CSV Gather",
                            Constants.DRIVER,
                            is_distributed=False)
    p.add_input_file_type(FileTypes.CHUNK, "cjson_in", "GCHUNK Json",
                          "Gathered CHUNK Json with CSV chunk key")

    p.add_output_file_type(FileTypes.CSV, "csv_out",
                           "CSV",
                           "Gathered CSV", "gathered")

    # Only need to add to argparse layer for the commandline
    p.arg_parser.add_str(Constants.OPT_CHUNK_KEY,
                         "chunk_key",
                         "$chunk.csv_id",
                         "Chunk key",
                         "Chunk key to use (format $chunk.{chunk-key}")

    return p


def args_runner(args):
    return run_main_gather_csv(args.cjson_in, args.csv_out, args.chunk_key)


def rtc_runner(rtc):
    return run_main_gather_csv(rtc.task.input_files[0], rtc.task.output_files[0], Constants.CHUNK_KEY)


def main(argv=sys.argv):
    return pbparser_runner(argv[1:],
                           get_parser(),
                           args_runner,
                           rtc_runner,
                           log,
                           setup_log)


if __name__ == '__main__':
    sys.exit(main())

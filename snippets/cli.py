#!/usr/bin/python3
from argparse import ArgumentParser
import logging
import os
import sys
from evolution_strategy import EvolutionaryStrategy
from decouple import config
from aerialist.px4 import file_helper

logger = logging.getLogger(__name__)


def arg_parse():
    main_parser = ArgumentParser(
        description="UAV Test Generator",
    )
    subparsers = main_parser.add_subparsers()
    parser = subparsers.add_parser(name="generate", description="generate tests")
    parser.add_argument("test", help="initial test description file address")

    parser.add_argument(
        "budget",
        type=int,
        help="test generation budget (total number of simulations allowed)",
    )

    args = main_parser.parse_args()
    return args


def config_loggers():
    os.makedirs("logs/", exist_ok=True)
    logging.basicConfig(
        level=logging.DEBUG,
        filename="logs/debug.txt",
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )

    root = logging.getLogger()
    # terminal logs
    c_handler = logging.StreamHandler()
    c_handler.setLevel(logging.INFO)
    c_format = logging.Formatter("%(name)s - %(levelname)s - %(message)s")
    c_handler.setFormatter(c_format)
    root.addHandler(c_handler)

    # file logs
    f_handler = logging.FileHandler("logs/info.txt")
    f_handler.setLevel(logging.INFO)
    f_format = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    f_handler.setFormatter(f_format)
    root.addHandler(f_handler)


if __name__ == "__main__":
    config_loggers()
    try:
        args = arg_parse()

        generator = EvolutionaryStrategy(case_study_file=args.test)
        test_cases = generator.generate(args.budget)
        results = generator.save_results()

        print("------------------------------------")
        print("Test cases generated successfully, check the results in: ", results)
        print("------------------------------------")
        if config("AGENT") == "k8s":
            file_helper.upload_dir(
                results, f'{config("WEBDAV_UP_FLD")}generated_tests/'
            )

    except Exception as e:
        logger.exception("program terminated:" + str(e), exc_info=True)
        sys.exit(1)

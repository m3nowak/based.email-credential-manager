import argparse

def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description='Based Email Credential Manager',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        '-c', '--config-path',
        help='Path to configuration file',
        default='/etc/based_email_cm/conf.yaml',
    )
    return parser
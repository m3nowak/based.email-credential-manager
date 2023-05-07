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
    parser.add_argument('--http-dmz', help='Run the HTTP DMZ service', action='store_true')
    parser.add_argument('--nats-dmz', help='Run the NATS DMZ service', action='store_true')
    parser.add_argument('-p', '--port', help='Port to run the HTTP DMZ service on', default=8080, type=int)
    return parser
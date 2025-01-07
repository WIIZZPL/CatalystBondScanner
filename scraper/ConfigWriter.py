from configparser import ConfigParser

config = ConfigParser()

config['OUTGOING'] = {
    'max_awaiting': 5,
    'timeout': 0.1
}

config['DEFAULT'] = {
    'max_awaiting': 5,
    'timeout': 0.1
}

config['gpwcatalyst.pl'] = {
    'max_awaiting': 5,
    'timeout': 0.1
}

with open('config.ini', 'w') as f:
    config.write(f)
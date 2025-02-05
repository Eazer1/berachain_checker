import random

from web3 import Web3
from loguru import logger
from time import sleep
from threading import Thread

from cfg import *

def get_random_proxy():
    with open('proxies.txt', 'r') as file:
        lines = file.readlines()
        if not lines:
            raise ValueError("Файл с прокси пуст!")
        
        random_line = random.choice(lines).strip()
        splited_data = random_line.split(':')
        
        if len(splited_data) != 4:
            raise ValueError("Некорректный формат прокси в файле! Должно быть ip:port:log:pass")
        
        ip, port, log, password = splited_data
        formatted_proxy = f'{log}:{password}@{ip}:{port}'
        
        return {
            'http': f'http://{formatted_proxy}',
            'https': f'http://{formatted_proxy}'
        }
    
def get_kwargs():
    proxy = get_random_proxy()
    kwargs={'timeout': 120,'proxies': proxy}
    return kwargs
    
def web3connect_with_proxy():
    while True:
        try:
            web3 = Web3(Web3.HTTPProvider(NODE_RPC, request_kwargs=get_kwargs()))
            if web3.is_connected() == True:
                return web3
        except Exception as e:
            print(f'[web3connect_proxy] Error {e}')

def check_balance(address):
    address = Web3.to_checksum_address(address)
    

    while True:
        try:
            web3 = web3connect_with_proxy()
            balance = web3.eth.get_balance(address)
            if balance > 0:
                logger.success(f'[{address}] {balance/1000000000000000000}')
                with open(f'SUCCESS.txt', 'a', encoding='utf-8') as f:
                    f.write(f'{address};{balance/1000000000000000000}\n')
                
            break
        except Exception as e:
            print(e)

file_name = 'addresses'
accs_list = open(file_name + '.txt', 'r').read().splitlines()

for el in accs_list:
    splited_data = el.split(';')
    prkey = splited_data[0]

    Thread(target=check_balance, args=(prkey, )).start()
    sleep(0.1)

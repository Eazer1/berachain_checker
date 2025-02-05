import random
import requests
import json

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
            raise ValueError("Некорректный формат прокси в файле!")
        
        ip, port, log, password = splited_data
        formatted_proxy = f'{log}:{password}@{ip}:{port}'
        
        return {
            'http': f'http://{formatted_proxy}',
            'https': f'http://{formatted_proxy}'
        }

def check_allocation(address):
    while True:
        try:
            url = f'https://checker-api.berachain.com/whitelist/wallet/allocation?address={address.lower()}'

            headers = {
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'origin':'https://checker.berachain.com',
                'referer':'https://checker.berachain.com/',
            }

            resp = requests.get(url, headers=headers, proxies=get_random_proxy())
            #print(resp.status_code)
            #print(resp.text)
            if resp.status_code == 200:
                a = json.loads(resp.text)
                tokenQualified = a['tokenQualified']
                return tokenQualified
            
            else: sleep(5)
        except Exception as e:
            logger.error(f'[{address}] Error: {e}')
            sleep(5)

def check_nft(address):
    allocation = 0
    i = 0
    while True:
        try:
            url = f'https://checker-api.berachain.com/nfts?owner={address.lower()}&contractAddresses[]=0x495f947276749ce646f68ac8c248420045cb7b5e&contractAddresses[]=0xf17bb82b6e9cc0075ae308e406e5198ba7320545&contractAddresses[]=0x2c889a24af0d0ec6337db8feb589fa6368491146&contractAddresses[]=0x9e629d779be89783263d4c4a765c38eb3f18671c&contractAddresses[]=0xb4e570232d3e55d2ee850047639dc74da83c7067&contractAddresses[]=0x32bb5a147b5371fd901aa4a72b7f82c58a87e36d'

            headers = {
                'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36',
                'origin':'https://checker.berachain.com',
                'referer':'https://checker.berachain.com/',
            }

            resp = requests.get(url, headers=headers, proxies=get_random_proxy())
            #print(resp.status_code)
            #print(resp.text)
            if resp.status_code == 200:
                a = json.loads(resp.text)
                ownedNfts = a['ownedNfts']

                for nft in ownedNfts:
                    CA_address = nft['contract']['address']
                    CA_address = CA_address.lower()

                    if CA_address == '0x495f947276749ce646f68ac8c248420045cb7b5e':
                        name = nft['collection']['name']
                        if 'Bong Bears' in name:
                            allocation = allocation + NFTS[CA_address]
                            
                    else:
                        allocation = allocation + NFTS[CA_address]

                return allocation
            else: sleep(5)
        except Exception as e:
            logger.error(f'[{address}] Error: {e}')
            sleep(5)

def start(address):
    base_allocation = float(check_allocation(address))
    nft_allocation = float(check_nft(address))

    result = base_allocation + nft_allocation

    with open(f'SUCCESS.txt', 'a', encoding='utf-8') as f:
        f.write(f'{address};{result}\n')

    logger.success(f'[{address}] Allocation: {result}')

file_name = 'addresses'
accs_list = open(file_name + '.txt', 'r').read().splitlines()

for el in accs_list:
    splited_data = el.split(';')
    address = splited_data[0]

    Thread(target=start, args=(address, )).start()
    sleep(0.1)

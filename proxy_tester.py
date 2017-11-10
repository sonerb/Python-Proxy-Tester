import math
import os
import os.path
import requests
from threading import Thread
import sys
import time

timeout = 5
good_list = []


def verify_list(proxy_list, thread_number):
    global good_list, timeout
    working_list = []
    for prox in proxy_list:
        try:

            proxy_dict = {
                "http": "http://"+prox+"/",
            }

            r = requests.get("http://ipinfo.io/json", proxies=proxy_dict, timeout=timeout)
            site_code = r.json()
            ip = site_code['ip']
            print('[Thread:', thread_number, '] Current IP:', ip)
            print('[Thread:', thread_number, '] Proxy works:', prox)
            print('[Thread:', thread_number, '] match:', True if ip == prox.split(':')[0] else False)
            working_list.append(prox)
        except Exception as e:
            print('[Thread:', thread_number, '] Proxy failed', prox)
            print('[Thread:', thread_number, '] Proxy failed', e)
    print('[Thread:', thread_number, '] Working Proxies:', working_list)
    good_list += working_list


def get_proxy_list():
    directory = './'
    file = os.path.abspath(__file__)
    for i in sorted(range(len(file)), reverse=True):
        if '/' in file[i] or '\\' in file[i]:
            directory = file[:i+1]
            break
    file_list = os.listdir(directory)
    proxy_list = []
    for file in file_list:
        if len(file) > 12:
            if file[:8] == 'proxies_':
                    proxy_list.append(directory+file)
    return proxy_list


def get_proxies(files):
    proxy_list = []
    for file in files:
        for prox in open(file, 'r+').readlines():
            proxy_list.append(prox.strip())
    return proxy_list


def setup(number_threads):
    thread_amount = float(number_threads)
    proxy_list = get_proxies(get_proxy_list())
    amount = int(math.ceil(len(proxy_list)/thread_amount))
    proxy_lists = [proxy_list[x:x+amount] for x in range(0, len(proxy_list), amount)]
    if len(proxy_list) % thread_amount > 0.0:
        proxy_lists[len(proxy_lists)-1].append(proxy_list[len(proxy_list)-1])
    return proxy_lists


def start(threads):
    start_time = time.time()
    lists = setup(threads)
    thread_list = []
    count = 0
    for l in lists:
        thread_list.append(Thread(target=verify_list, args=(l, count)))
        thread_list[len(thread_list)-1].start()
        count += 1

    for x in thread_list:
        x.join()

    print('[All         ] Working Proxies:', good_list)

    f = open('good_proxies_list.txt', 'w+')
    to_write = ''
    for i in good_list:
        to_write += i+'\n'
    f.write(to_write)
    f.close()
    stop_time = time.time()
    print('[{0:.2f} seconds]'.format(stop_time-start_time))


if __name__ == "__main__":
    if len(sys.argv) > 1:
        start(sys.argv[1])
    else:
        start(input('How many threads you would like to test proxies with: '))

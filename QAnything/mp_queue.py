# from multiprocessing import Process
# import random
# import time
# import os
# def sleep(person):
#     '''
#     person:str
#     '''
#     print(f"进程{os.getpid()}")
#     t = random.randint(2,6)
#     time.sleep(t) 
#     print(f"sleep{t}s")

# if __name__=="__main__":
#     start = time.time()
#     # sleep("a")
#     # sleep("b")
#     t1 =Process(target=sleep,args=("a"))
#     t2 =Process(target=sleep,args=("b"))
#     t1.start()
#     t2.start()
#     t1.join()#加阻塞，让主进程等t1
#     t2.join()
#     end = time.time()
#     print(f"用时{end-start}")
import multiprocessing
import requests
from bs4 import BeautifulSoup
 
# 生产者函数：爬取网页内容，并将内容放入队列中
def producer(url, queue):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    # 假设需要爬取网页中的所有链接
    links = [link.get('href') for link in soup.find_all('a')]
    queue.put(links)
 
# 消费者函数：从队列中获取数据，并进行处理
def consumer(queue):
    while True:
        data = queue.get()
        if data == 'STOP':
            break
        for link in data:
            # 在这里可以进行进一步处理，比如访问链接、提取信息等
            print("Processing link:", link)
 
if __name__ == "__main__":
    # 创建消息队列
    queue = multiprocessing.Queue()
 
    # 启动生产者进程
    producer_process = multiprocessing.Process(target=producer, args=('https://cloud.baidu.com/article/3262453', queue))
    producer_process.start()
 
    # 启动消费者进程
    consumer_process = multiprocessing.Process(target=consumer, args=(queue,))
    consumer_process.start()
 
    # 等待生产者进程结束
    producer_process.join()
 
    # 向队列中放入结束信号
    queue.put('STOP')
 
    # 等待消费者进程结束
    consumer_process.join()
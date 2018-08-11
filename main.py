#!-*-coding:utf-8-*-
# !@Date: 2018/8/10 12:55
# !@Author: Liu Rui
# !@github: bigfoolliu

"""
udp chatter

多线程, tkinter GUI

"""
from tkinter import *
import time
import threading
from multiprocessing import Queue
import socket

# 获取本机电脑名
local_name = socket.getfqdn(socket.gethostname())
# 获取本机ip
local_ip = socket.gethostbyname(local_name)
local_port = 999

target_address = ["0.0.0.0", 0]


class AppUI(object):
	def __init__(self):
		global target_address
		# 文本框显示时间头部信息
		self.head_message = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

		# 顶层窗口
		self.tk = Tk()
		self.tk.title("udp聊天器")

		# 设置上下右frame作为容器
		self.frame_top = Frame(self.tk, width=350, height=340, bg="white")
		self.frame_down = Frame(self.tk, width=350, height=50, bg="white")
		self.frame_right = Frame(self.tk, width=200, height=400, bg="#C4DCEF")

		# 设置容器的位置
		self.frame_top.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + W + E)
		self.frame_down.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + W + E)
		self.frame_right.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky=N + S + W + E)
		self.frame_top.grid_propagate(0)  # 强制让frame的大小不变
		self.frame_down.grid_propagate(0)
		self.frame_right.grid_propagate(0)
		# 设置容器行列的长度比重
		self.frame_top.grid_rowconfigure(0, weight=1)
		self.frame_top.grid_columnconfigure(0, weight=1)
		self.frame_down.grid_columnconfigure(0, weight=3)
		self.frame_down.grid_columnconfigure(1, weight=1)
		self.frame_down.grid_rowconfigure(0, weight=1)
		self.frame_right.grid_rowconfigure(2, weight=1)
		self.frame_right.grid_rowconfigure(5, weight=6)
		self.frame_right.grid_columnconfigure(1, weight=1)

		# 设置几个元素
		self.text_display = Text(self.frame_top, bg="#549B78")
		self.entry_message = StringVar()  # 输入的消息
		self.entry_input = Entry(self.frame_down, bg="#D57E26", textvariable=self.entry_message)
		self.button_send = Button(self.frame_down, bg="#EFDCD3", text="Send", command=self.display_message)
		self.label_target_ip = Label(self.frame_right, bg="#C4DCEF", text="目标IP:", font=("arial", 10))
		self.label_target_port = Label(self.frame_right, bg="#C4DCEF", text="端口:", font=("arial", 10))
		self.label_local_ip = Label(self.frame_right, bg="#C4DCEF", text="本地IP:", font=("arial", 10))
		self.label_local_port = Label(self.frame_right, bg="#C4DCEF", text="端口:", font=("arial", 10))
		self.target_ip = StringVar(value=target_address[0])  # 目标ip
		self.target_port = IntVar(value=target_address[1])  # 目标端口
		self.local_ip = StringVar(value=local_ip)  # 本地ip
		self.local_port = IntVar(value=local_port)  # 本地端口
		self.entry_target_ip = Entry(self.frame_right, bg="#E1E4D3", textvariable=self.target_ip)
		self.entry_target_port = Entry(self.frame_right, bg="#E1E4D3", textvariable=self.target_port)
		self.entry_local_ip = Entry(self.frame_right, bg="#E1E4D3", textvariable=self.local_ip)
		self.entry_local_port = Entry(self.frame_right, bg="#E1E4D3", textvariable=self.local_port)

		# 设置元素的位置
		self.text_display.grid(padx=5, pady=5, sticky=N + S + W + E)
		self.entry_input.grid(row=0, column=0, padx=0, pady=5, sticky=N + S + W + E)
		self.button_send.grid(row=0, column=1, padx=0, pady=5, sticky=N + S + W + E)
		self.label_target_ip.grid(row=0, column=0, padx=5, pady=5, sticky=N + S + E)
		self.label_target_port.grid(row=1, column=0, padx=5, pady=5, sticky=N + S + E)
		self.label_local_ip.grid(row=3, column=0, padx=5, pady=5, sticky=N + S + E)
		self.label_local_port.grid(row=4, column=0, padx=5, pady=5, sticky=N + S + E)
		self.entry_target_ip.grid(row=0, column=1, padx=5, sticky=W + E)
		self.entry_target_port.grid(row=1, column=1, padx=5, sticky=W + E)
		self.entry_local_ip.grid(row=3, column=1, padx=5, sticky=W + E)
		self.entry_local_port.grid(row=4, column=1, padx=5, sticky=W + E)

		# 建一个udp socket用于通信
		self.udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

		# 获取目的主机地址以及本地主机地址
		self.target_address = (self.target_ip.get(), self.target_port.get())
		self.local_address = (self.local_ip.get(), self.local_port.get())

		# 绑定本地地址
		self.udp_socket.bind(self.local_address)

		# 开一个线程持续接收消息
		threading_receive = threading.Thread(target=self.receive_message)
		threading_receive.setDaemon(True)  # 接收消息线程设置为守护线程,当主线程结束,该线程也会被杀死
		threading_receive.start()

		# 建一个队列用来存储发送的消息
		self.queue_send_message = Queue()

		self.tk.mainloop()
		self.udp_socket.close()

	def display_message(self):
		"""将自己发送的消息显示到文本框"""
		global target_address
		target_address = (self.target_ip.get(), self.target_port.get())

		self.text_display.insert(END, "I" + self.head_message + "\n", "green")  # 显示时间头

		entry_message = self.entry_message.get()  # 接收动态获取的输入消息
		self.text_display.insert(END, entry_message + "\n")  # 文本框显示输入的消息
		self.entry_message.set("")  # 输入信息框上传后设置为空

		self.queue_send_message.put(entry_message)  # 将输入的消息存储进队列
		try:
			self.target_address = target_address  # 获取新的目标地址
			print(self.target_address)
			send_data = str(self.local_address) + self.head_message + ":\n" + self.queue_send_message.get() + "\n\n"
			self.udp_socket.sendto(send_data.encode("utf-8"), self.target_address)
			print("消息发送成功...")
		except:
			print("目标地址IP不对,需要重新输入.")

	def receive_message(self):
		"""接收消息,需要单独的一个开一个进程,这里接收的消息要用队列,而且接收只要打开窗口就会执行"""
		while True:
			print("接收进程进行中")
			try:
				receive_data = self.udp_socket.recvfrom(1024)
				receive_data = receive_data[0].decode("utf-8")
				self.text_display.insert(END, str(self.target_address) + self.head_message + ":\n", "green")
				self.text_display.insert(END, receive_data + "\n\n")
			except:
				print("接收消息失败.")
			time.sleep(1)  # 每隔一秒更新一次接收消息


if __name__ == '__main__':
	AppUI()

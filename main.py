import logging
import argparse
import time
import psutil
import requests
import sys
import os
import plotext as plt
import shutil

logging.basicConfig(
    filename='sysmon.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'    
)

    
########################
# Переменные для идемподентности алертов
########################


is_alert_disk_active = False
is_alert_ram_active = False
is_alert_cpu_active = False

disk_history = []
cpu_history = []
ram_history = []    


def send_alert (token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': message})
        logging.info(f"Alert sent: {message}")
        
    except Exception as e:
        logging.error(f"failed to send alert: {e}")
              
       
        
def check_system (disk_threshold, cpu_threshold, ram_threshold, token, chat_id):
    # Данные диска
    disk_usage = psutil.disk_usage('/')
        
    disk_percent = disk_usage.percent
    
    # Данные RAM
    ram_percent = psutil.virtual_memory().percent

    # Данные CPU
    cpu_percent = psutil.cpu_percent(interval=1)

    #Есть ли алерт
    is_alert = False
    alerts = []
    
    global is_alert_ram_active
    global is_alert_cpu_active
    global is_alert_disk_active
    
    #Для вывода графиков
    global disk_history
    global cpu_history 
    global ram_history 
    
    
    def draw_plot(disk_percent, cpu_percent, ram_percent):
        ram_history.append(ram_percent)
        if len (ram_history) > 100:
            ram_history.pop(0)
        
        
        cpu_history.append(cpu_percent)
        if len (cpu_history) > 100:
            cpu_history.pop(0)
        
        disk_history.append(disk_percent)
        if len(disk_history) > 100:
            disk_history.pop(0)
        
                
        os.system('cls') # clear для linux
            
        plt.clear_data()
        
        plt.plot(cpu_history, color="red", label="CPU")
        plt.plot(ram_history, color="blue", label="RAM")
        plt.plot(disk_history, color="green", label="Disk")
                 
        plt.ylim(0, 100)
        plt.title("System Load")
        #plt.grid(True)
        plt.show()        
    draw_plot(cpu_percent, ram_percent, disk_percent)
    
    
    # Отсылаем алерты в TG, если > threshold
    if disk_percent > disk_threshold and is_alert_disk_active == False:
        msg = f"⚠️ Disk usage high: {disk_percent:.1f}%"
        print (msg)
        is_alert = True
        alerts.append(msg)
        is_alert_disk_active = True
  
    elif disk_percent < disk_threshold and is_alert_disk_active == True:
        msg = "✅ Disk Alert Resolved"
        alerts.append(msg)
        print(msg)
        is_alert_disk_active = False
        
          
    if ram_percent > ram_threshold and is_alert_ram_active == False:
        msg = f"⚠️ Ram usage high: {ram_percent:.1f}%"
        print (msg)
        is_alert = True
        alerts.append(msg)
        is_alert_ram_active = True
        
    elif ram_percent < ram_threshold and is_alert_ram_active == True:
        msg = "✅ RAM Alert Resolved"
        alerts.append(msg)
        print(msg)
        is_alert_ram_active = False
    
        
    if cpu_percent > cpu_threshold and is_alert_cpu_active == False:
        msg = f"⚠️ CPU usage high: {cpu_percent:.1f}"
        is_alert = True
        alerts.append(msg)
        is_alert_cpu_active = True
  
    elif cpu_percent < cpu_threshold and is_alert_cpu_active == True:
        msg = "✅ CPU Alert Resolved"
        alerts.append(msg)
        is_alert_cpu_active = False    
    
    
    print("\033[1;36m" + "=" * shutil.get_terminal_size().columns + "\033[0m")
    print (f"Disk usage: {disk_percent:>10.1f}% | RAM usage: {ram_percent:>10.1f}% | CPU usage: {cpu_percent:>10.1f}%".center(shutil.get_terminal_size().columns))
    print("\033[1;36m" + "=" * shutil.get_terminal_size().columns + "\033[0m")

    if token and chat_id and alerts:
            for alert in alerts:
                send_alert (token, chat_id, alert)
            
            
def main():
    parser = argparse.ArgumentParser(description="System monitoring")
    parser.add_argument ('--interval', type=int, default=60, help='Check interval in seconds')
    parser.add_argument ('--disk-threshold', type=int, default=90, help='Disk usage alert threshold (%)')
    parser.add_argument ('--cpu-threshold', type=int, default=90, help='CPU usage alert threshold (%)')
    parser.add_argument ('--ram-threshold', type=int, default=80, help='RAM usage alert threshold (%)')
    parser.add_argument ('--telegram-bot-token', type=str, help='Telegram bot token (optional)')
    parser.add_argument ('--chat-id', type=str, help="Telegram chat ID (optional)")
    
    args = parser.parse_args()
        
    print (f"Starting sysmon... (Interval: {args.interval} sec.)")
    logging.info("sysmon started")
    
    try:
        while True:
            check_system(args.disk_threshold,
                         args.cpu_threshold,
                         args.ram_threshold,
                         args.telegram_bot_token,
                         args.chat_id
            )

            
            time.sleep(1) #args.interval
    except KeyboardInterrupt:
        print("\nStopping sysmon...")
        logging.info ("sysmon stopped")
        sys.exit(0)
    
if __name__ == "__main__":  
    
    main()
        
        
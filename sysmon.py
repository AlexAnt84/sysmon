import logging
import argparse
import time
import psutil
import requests
import sys
import os
import plotext as plt
import shutil


class MonitoringState:
    # Состояние алертов и история для отрисовки графиков
    def __init__(self):
        self.is_alert_disk_active = False
        self.is_alert_cpu_active = False
        self.is_alert_ram_active = False
        self.disk_history = []
        self.cpu_history = []
        self.ram_history = []    



logging.basicConfig(
    filename='sysmon.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'    
)
    

def collect_metrics():
    return{
        'disk': psutil.disk_usage('/').percent,        
        'cpu': psutil.cpu_percent(interval=1),
        'ram': psutil.virtual_memory().percent
    }

def update_history(history, value, max_len=100):
    history.append(value)
    if len(history) > max_len:
        history.pop(0)


def process_alerts (disk_percent, cpu_percent, ram_percent, disk_threshold, cpu_threshold, ram_threshold, alerts, state):
    # Отсылаем алерты в TG, если > threshold
    if disk_percent > disk_threshold and state.is_alert_disk_active == False:
        msg = f"⚠️ Disk usage high: {disk_percent:.1f}%"
        print (msg)
        alerts.append(msg)
        state.is_alert_disk_active = True
    
    elif disk_percent < disk_threshold and state.is_alert_disk_active == True:
        msg = "✅ Disk Alert Resolved"
        alerts.append(msg)
        print(msg)
        state.is_alert_disk_active = False
            
            
    if ram_percent > ram_threshold and state.is_alert_ram_active == False:
        msg = f"⚠️ Ram usage high: {ram_percent:.1f}%"
        print (msg)
        alerts.append(msg)
        state.is_alert_ram_active = True
            
    elif ram_percent < ram_threshold and state.is_alert_ram_active == True:
        msg = "✅ RAM Alert Resolved"
        alerts.append(msg)
        print(msg)
        state.is_alert_ram_active = False
        
            
    if cpu_percent > cpu_threshold and state.is_alert_cpu_active == False:
        msg = f"⚠️ CPU usage high: {cpu_percent:.1f}"
        alerts.append(msg)
        state.is_alert_cpu_active = True
    
    elif cpu_percent < cpu_threshold and state.is_alert_cpu_active == True:
        msg = "✅ CPU Alert Resolved"
        alerts.append(msg)
        state.is_alert_cpu_active = False    


def send_alert (token, chat_id, message):
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    
    try:
        requests.post(url, data={'chat_id': chat_id, 'text': message})
        logging.info(f"Alert sent: {message}")
        
    except Exception as e:
        logging.error(f"failed to send alert: {e}")
              
       
        
def check_system (disk_threshold, cpu_threshold, ram_threshold, token, chat_id, state):
    
    #Собираем метрики
    metrics = collect_metrics()
    disk_percent = metrics['disk']
    cpu_percent = metrics['cpu']
    ram_percent = metrics['ram']    

    #Есть ли алерт
    alerts = []
    
    
    def draw_plot(disk_percent, cpu_percent, ram_percent):
        
        update_history(state.disk_history, disk_percent)
        update_history(state.cpu_history, cpu_percent)
        update_history(state.ram_history, ram_percent)
        
        
        if sys.platform == "win32":
            os.system('cls')
        else:
            os.system('clear')  # clear для linux
            
        plt.clear_data()
        
        plt.plot(state.disk_history, color="green", label="Disk")
        plt.plot(state.cpu_history, color="red", label="CPU")
        plt.plot(state.ram_history, color="blue", label="RAM")
                 
        plt.ylim(0, 100)
        plt.show()        
        
    # def render_plot ()
    draw_plot(disk_percent, cpu_percent, ram_percent)
    

            
    process_alerts(disk_percent,cpu_percent,ram_percent,disk_threshold,cpu_threshold,ram_threshold, alerts, state)
    
   
    
    
    print("\033[1;36m" + "=" * shutil.get_terminal_size().columns + "\033[0m")
    print (f"Disk usage: {disk_percent:>10.1f}% | CPU usage: {cpu_percent :>10.1f}% | RAM usage: {ram_percent :>10.1f}% ".center(shutil.get_terminal_size().columns))
    print("\033[1;36m" + "=" * shutil.get_terminal_size().columns + "\033[0m")

    if token and chat_id and alerts:
            for alert in alerts:
                send_alert (token, chat_id, alert)
            
            
def main():
    parser = argparse.ArgumentParser(description="System monitoring")
    parser.add_argument ('--interval', type=int, default=1, help='Check interval in seconds')
    parser.add_argument ('--disk-threshold', type=int, default=90, help='Disk usage alert threshold (%)')
    parser.add_argument ('--cpu-threshold', type=int, default=90, help='CPU usage alert threshold (%)')
    parser.add_argument ('--ram-threshold', type=int, default=80, help='RAM usage alert threshold (%)')
    parser.add_argument ('--telegram-bot-token', type=str, help='Telegram bot token (optional)')
    parser.add_argument ('--chat-id', type=str, help="Telegram chat ID (optional)")
    
    args = parser.parse_args()
    state = MonitoringState()
    
        
    print (f"Starting sysmon... (Interval: {args.interval} sec.)")
    logging.info("sysmon started")
    
    try:
        while True:
            check_system(args.disk_threshold,
                         args.cpu_threshold,
                         args.ram_threshold,
                         args.telegram_bot_token,
                         args.chat_id,
                         state
            )

            
            time.sleep(args.interval)
    except KeyboardInterrupt:
        print("\nStopping sysmon...")
        logging.info ("sysmon stopped")
        sys.exit(0)
        
if __name__ == "__main__":  
    main()      

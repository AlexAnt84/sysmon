import psutil
import time

#Собирает метрики, ведет историю
class MetricsCollector:
    def __init__(self, history_len=3):
        self.history_len = history_len
        self.history = {
            'disk': [],
            'cpu': [],
            'ram': []
        }

        
    
    def collect(self ):
        metrics = {
            'disk': psutil.disk_usage('/').percent,
            'cpu': psutil.cpu_percent(interval=1),
            'ram': psutil.virtual_memory().percent
        }
        
        #Обновляем историю
        for key, value in metrics.items():
            self.history[key].append(value)
            if len(self.history[key]) > self.history_len:
                self.history[key].pop(0)
        
        return metrics
    
class AlertManager:
    def __init__(self, disk_threshold=80, cpu_threshold=80, ram_threshold=80):

        self.disk_threshold = disk_threshold
        self.cpu_threshold = cpu_threshold
        self.ram_threshold = ram_threshold
        
        self.thresholds = {
            'disk': self.disk_threshold,
            'cpu': self.cpu_threshold,
            'ram': self.ram_threshold
        }
        
            
        self.is_active_flags = {
            'disk' : False,
            'cpu' : False,
            'ram' : False
        }  
    
    def process_alerts(self, metrics , hysteresis = 5 ):
        
        alerts = []
        
        for key, value in metrics.items():
            
            if value > self.thresholds[key] and not self.is_active_flags[key]:
                msg = f"⚠️ {key} usage high: {value:.1f}%"
                self.is_active_flags[key] = True
                alerts.append(msg)
            #disk_percent  <= self.disk_threshold - hysteresis and self.is_disk_alert_active:    
            elif value <= self.thresholds[key] - hysteresis and self.is_active_flags[key]:
                msg = f"✅ {key} alert resolved. Current value: {value:.1f}"
                self.is_active_flags[key] = False
                alerts.append(msg)
        
        return alerts            
    

class TerminalRenderer:
    def __init__(self, width=50):
        self.width = width
        
    def _get_color(self, value, threshold=80):
        if value > threshold:
            return '\033[91m' #Красный
        if value > threshold - 20:
            return '\033[93m' #Желтый
        else:
            return '\033[92m' #Зеленый
    
    def _reset_color(self):
        return '\033[0m' # Сброс цвета
    
    def render_bar(self, label, value):
        value = max(0, min(100, value))

        filled = int(self.width * value / 100)
        bar = '█' * filled + '░' * (self.width - filled)
        
        
        color = self._get_color(value)
        reset = self._reset_color()
        
        return f"{label:4}: {color}{bar}{value:.1f}% {reset}"
    
    def render (self, metrics):
        """Полная панель из метрик"""
        lines = []
        lines.append("📊 System Monitor 2.0")
        lines.append("=" * (self.width + 15))
        lines.append(self.render_bar("Disk", metrics['disk']))
        lines.append(self.render_bar("CPU", metrics['cpu']))
        lines.append(self.render_bar("RAM", metrics['ram']))
        lines.append("=" * (self.width + 15))
        return "\n".join(lines)
        

        
def main():
    collector = MetricsCollector(history_len=5)
    
    alert_manager = AlertManager(
        disk_threshold = 40,
        cpu_threshold = 40,
        ram_threshold = 40
    )
      
    renderer = TerminalRenderer(width=100)  
      
    try:
        while True:
            metrics = collector.collect()
            # alerts = alert_manager.process_alerts(
            #     metrics['disk'],
            #     metrics['cpu'],
            #     metrics['ram']
            # )
            
            alerts = alert_manager.process_alerts(metrics)
            
            
            
            # if alerts:
            #     for alert in alerts: 
            #         print(alert)    
                    
            print(renderer.render(metrics))       
            time.sleep(2)
            print("\033[2J\033[H", end="")
            
    except KeyboardInterrupt:
        print("\n Stopping sysmon...")



if __name__=='__main__':
    main()
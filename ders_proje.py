import os
import json
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime
import time

# Değişiklikleri takip eden özel bir event handler sınıfı
class ChangeHandler(FileSystemEventHandler):
    def _init_(self, log_file):
        self.log_file = log_file
        self.change_buffer = []  # Değişiklikleri geçici olarak depolamak için bir liste

    def log_change(self, event):
        change = {
            "event_type": event.event_type,
            "src_path": event.src_path,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.change_buffer.append(change)  # Değişikliği tamponda biriktir

    def on_created(self, event):
        self.log_change(event)

    def on_deleted(self, event):
        self.log_change(event)

    def on_modified(self, event):
        self.log_change(event)

    def on_moved(self, event):
        self.log_change(event)

    def save_changes_to_log(self):
        # Eğer tamponda değişiklikler varsa, bunları dosyaya kaydet
        if self.change_buffer:
            with open(self.log_file, "a") as f:
                for change in self.change_buffer:
                    f.write(json.dumps(change) + "\n")
            self.change_buffer = []  # Tamponu temizle

if _name_ == "_main_":
    watch_dir = "/home/linux/bsm/test"
    log_file = "/home/linux/bsm/logs/changes.json"

    # İzlenecek dizin varsa oluştur, yoksa hata verme
    if not os.path.exists(watch_dir):
        os.makedirs(watch_dir)

    event_handler = ChangeHandler(log_file)
    observer = Observer()
    observer.schedule(event_handler, watch_dir, recursive=True)
    observer.start()

    try:
        print(f"Watching directory: {watch_dir}")
        # 5 saniyelik aralıklarla değişiklikleri kaydet
        while True:
            time.sleep(5)  # CPU kullanımını düşürmek için bekle
            event_handler.save_changes_to_log()  # Değişiklikleri dosyaya kaydet
    except KeyboardInterrupt:
        observer.stop()

    observer.join()

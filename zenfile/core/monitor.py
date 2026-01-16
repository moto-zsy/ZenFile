from watchdog.events import FileSystemEventHandler

class FileMonitor(FileSystemEventHandler):
    def __init__(self, organizer):
        self.organizer = organizer

    def on_modified(self, event):
        if not event.is_directory:
            self.organizer.process_file(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self.organizer.process_file(event.dest_path)

    def on_created(self, event):
        if not event.is_directory:
            self.organizer.process_file(event.src_path)
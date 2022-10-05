import sys
from typing import Dict, Any


from snippets import dict_updater


class PrettyPrinter:
    _PRINTERS = []
    _DEFAULT_PRINTER = None
    
    def __new__(cls):
        instance = super().__new__(cls)
        cls._PRINTERS.append(instance)
        return instance
    
    @classmethod
    def _get_default(cls):
        if cls._DEFAULT_PRINTER is None:
            cls._DEFAULT_PRINTER = cls()
        return cls._DEFAULT_PRINTER
    
    def __init__(self, debug: bool = False, target_pipe = sys.stdout, defaults: Dict = {}, **kw):
        self.pipe = target_pipe
        self.debug = debug
        self.defaults = {'header_prefix':'|+|', 'converter':str}
        self.defaults.update(dict_updater(defaults, kw))
    
    def set_defaults(self, new_defaults: Dict):
        self.defaults = new_defaults
    
    def update_defaults(self, updater: Dict):
        self.defaults.update(updater)
    
    def make_info(self, header_text: str, header_prefix: str, info_entries: Dict[str,Any], *, with_header: bool = True, converter = str, **kw):
        head = "{header_prefix}{header_text}".format(header_prefix=header_prefix, header_text=header_text)
        max_name_length = len(max(info_entries.keys(), key=len))
        entries = ["{prefix}{entry}".format(prefix=" "*len(header_prefix), entry="{} : {}".format(name.ljust(max_name_length), converter(value))) for name, value in info_entries.items()]
        return [head]+entries if with_header else entries
    
    def print_info(self, header_text: str, info_entries: Dict[str,Any], **kw):
        kwargs = dict_updater(self.defaults, dict_updater({'header_text':header_text, 'info_entries':info_entries}, kw))
        lines = self.make_info(**kwargs)
        self.pipe.write("\n".join(lines)+"\n")
        self.pipe.flush()
    
    def print(self, header_text: str, info_entries: Dict[str,Any], *args, **kw):
        return self.print_info(header_text, info_entries, *args, **kw)
    
    def print_debug(self, header_text: str, info_entries: Dict[str,Any], *args, **kw):
        if self.debug:
            self.print_info(header_text, info_entries, *args, **kw)

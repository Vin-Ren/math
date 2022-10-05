import math
import re

from typing import Union


dict_updater = lambda base,updater:(lambda dbase,dupdt:[dbase.update(dupdt), dbase][-1])(base.copy(), updater)

remove_illegal_name_characters = lambda name: re.sub(r"[/\\:*?<>|\"]", '', name)
remove_illegal_name_characters_except_slashes = lambda name: re.sub(r"[:*?<>|\"]", '', name)


def metric_size_formatter(value: int, suffix: str = 'B', decimal_places: int = 2, factor: Union[int, float] = 1024.0):
    formattable_str = "{%s:.%sf} {unit}{suffix}" % ('value', decimal_places)
    for unit in ['','K','M','G','T','P','E','Z']:
        if abs(value) < factor:
            return formattable_str.format(value=value, unit=unit, suffix=suffix)
        value /= factor
    return formattable_str.format(value=value, unit='Y', suffix=suffix)


def make_progress_bar(value: int, length: int = 40, title: str = ' ', value_min = 0.0, value_max = 1.0, prefix: str = '', suffix: str = ''):
    blocks = ["", "▏","▎","▍","▌","▋","▊","▉","█"]
    lsep, rsep = "▏", "▕"
    
    value = min(max(value, value_min), value_max)
    prog_percentage = (value-value_min)/float(value_max-value_min)
    
    visualized_size = prog_percentage*length
    completed_blocks_size = math.floor(visualized_size)
    in_progress_block_size = visualized_size-completed_blocks_size # value between 0-1, like a percentage.
    
    base = 0.125
    block_index = math.floor(in_progress_block_size/base)
    # print(value, prog_percentage, visualized_size, completed_blocks_size, in_progress_block_size, block_index)
    progress_bars = "█"*completed_blocks_size + blocks[block_index]
    filler_spaces = ' ' * length-len(progress_bars)
    progress = lsep+progress_bars+filler_spaces+rsep
    return "\r{title}{prefix}{bar}{value:.1f}%{suffix}".format(title=title, prefix=prefix, suffix=suffix, bar=progress, value=value*100)

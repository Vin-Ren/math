

class BaseMath:
    def __repr__(self):
        return "<ABC BaseMath Object>"
    
    def get_lines(self):
        return ["ABSTRACT BASE MATH OBJECT"]
    
    def get_str(self):
        return "\n".join(self.get_lines())
    
    def display(self, **kwargs):
        print(self.get_str(), **kwargs)
    
    def show(self, **kw):
        self.display(**kw)


class Int(BaseMath):
    def __init__(self, val:int):
        self.value=int(val)
    def __add__(self, other):
        return self.__class__(self.value+other.value)
    def __sub__(self, other):
        return self.__class__(self.value-other.value)
    def __mul__(self, other):
        if isinstance(other, Int):
            return self.__class__(self.value * other.value)
        elif isinstance(other, int):
            return self.__class__(self.value * other)
        else:
            return other.__class__.__mul__(other, self)
    def __rmul(self, other):
        if isinstance(other, (Int, int)):
            return self.__class__.__mul__(self, other)
        else:
            return other.__class__.__mul__(other, self)
    def __truediv__(self, other): # Supports scalar division only
        return self.__class__(self.value/other.value)
    def __repr__(self):
        return "<Int>"
    def get_lines(self):
        return [str(self.value)]

class Float(Int):
    def __init__(self, val:float):
        self.value=float(val)
    def __repr__(self):
        return "<Float>"


def convert_primitive_type(value):
    if isinstance(value,str):
        if value.__contains__(','):
            value=value.replace(',','')
        if value.isdigit():
            return Int(value)
        elif value.__contains__('.'):
            if value.replace('.', '').isdigit():
                if float(value) == int(float(value)):
                    return Int(value)
                return Float(value)
    
    if isinstance(value, int):
        return Int(value)
    elif isinstance(value, float):
        return Float(value)

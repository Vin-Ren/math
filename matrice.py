from base import BaseMath


# Exceptions
class MatriceError(Exception):
    pass

class InvalidMatrice(MatriceError):
    pass

class MatriceIncompatible(MatriceError):
    pass

class MatriceMethodNotImplemented(MatriceError, NotImplementedError):
    pass

class MatriceDataRequired(MatriceError):
    pass



#Primitive OPs

def multiply(ma,mb):
    # len(ma[0]) or len(mb)
    # must be the same for multiplication
    if len(ma[0])!=len(mb):
        raise MatriceIncompatible("A's column count is not equal B's row count. (%d!=%d)".format(len(ma[0]), len(mb)))
    mr=[[]]*len(ma)
    for i in range(len(ma)):
        mr[i] = [sum([mb[k][j]*ma[i][k] for k in range(len(ma[0]))]) for j in range(len(mb[0]))]
    return mr

def scalar_multiply(s,ma):
    if type(ma) == int:
        s,ma=ma,s
    return [[ma[i][j]*s for j in range(len(ma[0]))] for i in range(len(ma))]

def transpose(m):
    return [[m[j][i] for j in range(len(m))] for i in range(len(m[0]))]

def add(ma,mb):
    if not (len(ma) == len(mb) and len(ma[0]) == len(mb[0])):
        print(ma)
        print(mb)
        raise MatriceIncompatible("To Add or Subtract a matrice from another, their dimensions needs to be the same.")
    return [[ma[i][j]+mb[i][j] for j in range(len(ma[0]))] for i in range(len(ma))]

def sub(ma,mb):
    return add(ma, scalar_multiply(mb,-1))



# Wrapped

class Matrice(BaseMath):
    @staticmethod
    def validate_list(lst):
        if not isinstance(lst, list):
            raise InvalidMatrice("Matrice needs to be of type list[list].")
        if len(lst) == 0:
            return [[]]
        if isinstance(lst[0], (int, float)):
            lst = [lst]
        row_len=len(lst[0])
        for row in lst:
            if not isinstance(row, list):
                raise InvalidMatrice("Matrice needs to be of type list[list].")
            if len(row)!=row_len:
                raise InvalidMatrice("A matrice's column count must be constant across the rows.")
        return lst
    
    @staticmethod
    def to_immutable(lst):
        return tuple(tuple(row) for row in lst)
    
    @staticmethod
    def convert_to_ints(lst):
        return [[int(i) if i==int(i) else i for i in row] for row in lst]
    
    @classmethod
    def preprocess(cls, lst):
        return cls.to_immutable(cls.convert_to_ints(cls.validate_list(lst)))

    @classmethod
    def from_str(cls, s, column_delimiter=' ', row_delimiter='\n'):
        return cls([[float(i) for i in row.split(column_delimiter) if i] for row in s.split(row_delimiter)])

    def __init__(self, lst=None):
        self.lst = self.preprocess(lst)
    
    @property
    def order(self):
        return "%dx%d" % (self.rows, self.columns)
    
    @property
    def rows(self):
        return len(self.lst)
    
    @property
    def columns(self):
        return len(self.lst[0])
    
    def __getitem__(self, key):
        return self.lst[key]
    
    def __repr__(self):
        return "<%s Matrice>" % self.order
    
    def __eq__(self, other):
        return isinstance(other, Matrice) and self.order==other.order and self.lst==other.lst
    
    def __add__(self, other):
        return Matrice(add(self.lst, other.lst))
    
    def __sub__(self, other):
        return Matrice(sub(self.lst, other.lst))
    
    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return Matrice(scalar_multiply(other, self.lst))
        elif isinstance(other, Matrice):
            return Matrice(multiply(self.lst, other.lst))
        elif isinstance(other, list):
            return Matrice(multiply(self.lst, other))
        elif isinstance(other, BaseMath):
            return Matrice(scalar_multiply(other.value, self.lst))
        else:
            raise MatriceIncompatible("Operand is not compatible.")
    
    def __truediv__(self, other): # Supports scalar division only
        return self.__mul__(1/other)
    
    def __rmul__(self, other): # For expressions like "2*A" instead of "A*2"
        return self.__mul__(other)
    
    def transpose(self):
        return Matrice(transpose(self.lst))
    
    def determinant(self):
        if (self.order=='2x2'):
            return self[0][0]*self[1][1] - self[0][1]*self[1][0]
        elif (self.order=='3x3'):
            _sum=0
            for i in range(self.columns):
                line=1
                opposing_line=1
                for j in range(self.rows):
                    line*=self[j % self.rows][(i+j) % self.columns]
                    opposing_line*=self[-j % self.rows][(i+j) % self.columns]
                    # print(f"self[j%rows][(i+j)%cols]={self[j % self.rows][(i+j) % self.columns]} i={i} j={j} line={line}")
                    # print(f"inv => self[j%rows][(i+j)%cols]={self[-j % self.rows][(i+j) % self.columns]} i={i} j={j} line={opposing_line}")
                _sum+=line-opposing_line
            return _sum
        else:
            raise MatriceMethodNotImplemented("Determinant not Implemented for matrices bigger than 3x3.")
    
    def cofactor(self):
        if (self.order!='3x3'):
            raise MatriceMethodNotImplemented("Cofactor only available for matrice of size")
        arr = []
        for i in range(self.rows):
            row=[]
            for j in range(self.columns):
                curr_minor=Matrice([[el for rx, el in enumerate(row) if rx!=j] for ry,row in enumerate(self.lst) if ry!=i])
                # curr_minor.show() # Debug
                row.append(curr_minor.determinant()*(1 if (i+j)%2==0 else -1))
            arr.append(row)
        return Matrice(arr)
        
    
    def adjoint(self):
        if (self.order=='2x2'):
            return Matrice([[self[1][1], -self[0][1]], [-self[1][0], self[0][0]]])
        elif (self.order=='3x3'):
            return self.cofactor().transpose()
        else:
            raise MatriceMethodNotImplemented("Adjoint not implemented for matrices bigger than 3x3.")
    
    def inverse(self):
        try:
            determinant = self.determinant()
            adjoint = self.adjoint()
        except MatriceMethodNotImplemented as exc:
            raise MatriceDataRequired("Determinant and adjoint are required for inverse calculation.") from exc
        
        if (self.order in ['2x2', '3x3']):
            return 1/determinant * adjoint
        else:
            raise MatriceMethodNotImplemented("Inverse not Implemented for matrices bigger than 3x3.")
    
    def sum(self):
        "Get sum of all element in the matrice."
        return sum([element for row in self.lst for element in row]) # Flatten list and sum
    
    def get_lines(self):
        """ 
        Creates a string representation of the matrice. 
        
        Symbols:
        ┏   ┓
        ┃   ┃
        ┗   ┛
        """
        max_col_digit = [len(str(max([self.lst[j][i] for j in range(self.rows)], key=lambda x:len(str(x))))) for i in range(self.columns)]
        lines = ["┃ {} ┃".format("  ".join([str(i).center(max_col_digit[idx]) for idx,i in enumerate(row)])) for row in self.lst]
        lines.insert(0,"┏{}┓".format(" "*(len(lines[0])-2)))
        lines.append("┗{}┛".format(" "*(len(lines[0])-2)))
        return lines
    
    def display(self, **kwargs):
        print(self.get_str(), **kwargs)
    
    def show(self, **kwargs):
        return self.display(**kwargs)


def show(matrice:Matrice):
    matrice.show()


def init_matrice(print_matrice=True):
    print("Enter the matrice's elements, after entering all elements, press enter once more.")
    # row_c = int(input("Matrice A Row Count:"))
    rows = []
    while True:
        curr = input()
        if curr == '':
            break
        rows.append(curr)
    A=Matrice.from_str(s="\n".join(rows))
    if print_matrice:
        print(A, '\n', A.get_str(), sep='')
    return A


def center_lines(lst, diff, filler):
    bottom = diff//2
    top = diff-bottom
    lst = [filler]*top + lst + [filler]*bottom
    return lst


def visualize_operation(ma:Matrice,mb:Matrice,op, result_right=True):
    space_between_matrices = 5
    A_str = ma.get_lines()
    B_str = mb.get_lines()
    namespace={'A':ma, 'B':mb}
    exec('R=A{}B'.format(op),namespace)
    R_str = namespace['R'].get_lines()
    expression_str = []
    
    longer=max([len(B_str),len(A_str), len(R_str)])
    AB_longer = max([len(B_str),len(A_str)])
    if longer>len(A_str):
        diff=longer-len(A_str)
        filler_line="".center(len(A_str[0]))
        A_str = center_lines(A_str, diff, filler_line)
        # for i in range(diff):
        #     A_str.append(filler_line)
    if longer>len(B_str):
        diff=longer-len(B_str)
        filler_line="".center(len(B_str[0]))
        B_str = center_lines(B_str, diff, filler_line)
        # for i in range(diff):
        #     B_str.append(filler_line)
    if longer>len(R_str):
        diff=longer-len(R_str)
        filler_line="".center(len(R_str[0]))
        C_str = center_lines(C_str, diff, filler_line)
    OP_loc = (AB_longer//2)
    for i,line in enumerate(A_str):
        if i==OP_loc:
            if result_right:
                expression_str.append(line + op.center(space_between_matrices) + B_str[i] + "=".center(space_between_matrices) + R_str[i])
            else:
                expression_str.append(R_str[i] + "=".center(space_between_matrices)+ line + op.center(space_between_matrices)+B_str[i])
        else:
            if result_right:
                expression_str.append(line + "".center(space_between_matrices)+B_str[i]+"".center(space_between_matrices)+R_str[i])
            else:
                expression_str.append(R_str[i] + "".center(space_between_matrices)+ line + "".center(space_between_matrices)+B_str[i])
    print("\n".join(expression_str))
    return namespace['R']


if __name__ == '__main__':
    #Shorthands
    M=Matrice
    s=show
    m=init_matrice
    vop=visualize_operation
    
    A=Matrice([[1,2,3],[3,4,5],[5,6,7]])
    B=Matrice([[7,6,5],[5,4,3],[3,2,1]])
    C = init_matrice()


def diff(f):
	size = len(f) -1
	f_aux = []

	for i in range(len(f)):
		f_aux.append(f[i]*size)
		size -= 1

	return f_aux[:-1]

'''
f(x) = 2x³ + x² - 3x + 4
seria representado como
[2,1,-3,4]
'''

def calculate(f, x):
	y = 0
	size = len(f)-1
	for i in range(0,len(f)-1):
		y += (x**size)*f[i]
		size -=1

	y += f[-1]
	return y

# Bissecção para x² + 2x
def bissec(f,a,b,err):
	a_is_negative = True
	f_line = diff(f)

	if(calculate(f_line, a) * calculate(f_line, b) < 0):

		while(err < abs(b-a)):
			if(calculate(f,a) * calculate(f,(a+b)/2) < 0):
				b = (a+b)/2
			else:
				a = (a+b)/2
		return (a+b)/2


	else:
		return "Não possui raiz"

print(bissec([1,0,-9], -2, 60, 0.001))
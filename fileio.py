def read(filename):
	fd = open(filename,'r')
	out = fd.read()
	fd.close()
	return out
def readlines(filename, n):
	fd = open(filename,'r')
	out = ""
	for i in range(n):
		out = "%s%s"%(out,fd.readline())
	fd.close()
	return out
def readline(filename):
	return readlines(filename,1)
def write(filename, str):
	fd = open(filename,'w')
	fd.write(str)
	fd.close()
def append(filename,str):
	fd = open(filename,'a')
	fd.write(str)
	fd.close()

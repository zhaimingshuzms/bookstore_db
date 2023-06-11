import sys,os
print(os.getcwd())
sys.path.append(os.getcwd())
from be import serve

if __name__ == "__main__":
    serve.be_run()

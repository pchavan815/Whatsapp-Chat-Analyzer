import subprocess

try:
    # Attempt to install the geventhttpclient package
    subprocess.run(["pip", "install", "geventhttpclient"])
    print("geventhttpclient installed successfully!")
except subprocess.CalledProcessError as e:
    # If installation fails, print the error message
    print("Error installing geventhttpclient:")
    print(e)



#1 locust -f locust.py
# click on link , ex for users 50,5
# http (localhost link paste)

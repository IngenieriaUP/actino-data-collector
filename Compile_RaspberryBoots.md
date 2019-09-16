
# To compile when raspberry pi boots

### 1. Create the python file

#  

### 2. run:

#### $ sudo nano /etc/rc.local 

#  

### 3. Write this in rc.local:

$ sudo python /home/pi/sample.py 
#### (above exit 0)

#### then: ctrl + x, yes, enter

###  

###  4. run

#### $ sudo python /home/pi/sample.py &

#### (use the whole directiof of the file)

  

### 5. Reboot to test

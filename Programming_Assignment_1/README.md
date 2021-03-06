# Data Science Assignment #1  
# Apriori Pruning Algorithm

## 1. Environment
* OS : Windows 10
* Language : Python 2.7.12  
<br>  

## 2. How to build exe file

![](pic/01.jpg)  
(1) You need to install py2exe.  
Connect to the http://py2exe.org , and click 'downloads' button.  
<br>    
  
![](pic/02.jpg)
(2) Download 'py2exe-0.6.9.win32-py2.7.exe'.  
<br>  
  
![](pic/03.jpg)
(3) You can easily install it by clicking 'next' button.  
<br>    
  
![](pic/04.jpg)  
(4) Move to directory with apriori.py and setup.py.  
I uploaded the setup.py as well. You can use it like a Makefile.  
<br>    
  
![](pic/05.jpg)  
(5) insert the command.  
  
> $ python setup.py py2exe  
  
<br>

![](pic/06.jpg)  
(6) After that, you can get the exe file.

<br>    
  
![](pic/07.jpg)
(7) The exe file will be in the 'dist' folder.

<br>    
  
## 3. How to execute exe file

<br>

![](pic/08.jpg)
Move to directory with apriori.exe and input file.  
And insert the command.
  
> $ apriori.exe [minimum\_support] [input\_file\_name] [output\_file\_name]  
  
<br>

![](pic/09.jpg)  
You can get the answer.  

<br>    
  
## 4. How to test without exe file  
  
![](pic/10.jpg)  
If you don't want to install py2exe, or your environment can't execute exe file, (ex. OS X) you can easily test it by python command.  
Move to the folder with apriori.py and input file.  
And insert the command.  
  
> $ python apriori.py [minimum\_support] [input\_file\_name] [output\_file\_name]  

<br>    
  
## 5. This program passed the test.
  
![](pic/11.jpg)  


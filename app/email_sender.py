import smtplib



class ForgotPassword(object):

    def __init__(self):
        self.sender="aymen.m.rumi@gmail.com"
        self.password="******"
        self.server = smtplib.SMTP('smtp.gmail.com',587)

    def sendEmail(self,receiver,name,password):

        message="Hi {}\n\nYour password for ML Medical Application is {}\n\nBest Regards\nAymen Rumi".format(name,password)
        email = 'Subject: {}\n\n{}'.format("Forgot Password", message)
        self.server.starttls()

        self.server.login(self.sender,self.password)
        self.server.sendmail(self.sender,receiver,email)




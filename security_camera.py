import cv2
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from threading import Thread
import time
from email.mime.multipart import MIMEMultipart
import logging

camera = cv2.VideoCapture(0)
email = ''
receiver = ''
password = ''
start = 0

def send_mail(subject, text, image):
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(email, password)
    message = MIMEMultipart(text, "html")
    message["Subject"] = subject
    message["From"] = email
    message["To"] = receiver
    msgText = MIMEText(text, 'html')
    message.attach(msgText)
    try:
        with open(image, 'rb') as file:
            img = MIMEImage(file.read())
            img.add_header('Content-Disposition', 'attachment', filename=image)
            message.attach(img)
        server.sendmail(
            email, receiver, message.as_string()
        )
    except smtplib.SMTPException:
        logging.warning("Error! Unable to send email!")
    except Exception as e:
        print(e)
    server.close()
    

while camera.isOpened():
    ret, frame1 = camera.read()
    ret, frame2 = camera.read()
    diff = cv2.absdiff(frame1, frame2)
    gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5,5), 0)
    _, thresh = cv2.threshold(blur, 40, 255,cv2.THRESH_BINARY)
    dilated = cv2.dilate(thresh, None, iterations=5)
    contours, _ = cv2.findContours(dilated, cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
    cv2.drawContours(frame1, contours, -1, (0,255,255),2)
    for c in contours:
        if cv2.contourArea(c) > 8000:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(frame1,(x,y), (x+w,y+h), (0,0,255), 2)
            last = time.time() - start
            if last > 60:
                start = time.time()
                name = str(time.ctime()) + ".jpg"
                cv2.imwrite(name,frame1)
                thread = Thread(target = send_mail, args = ("Security camera", "Someone caught on camera! Look at the photo...", name))
                thread.start()
    cv2.imshow('Security camera', frame1)

    if cv2.waitKey(10) == ord('q'):
        break

cv2.destroyAllWindows()
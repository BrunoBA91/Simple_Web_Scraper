#! /usr/bin/python3

import urllib.request
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
import hashlib
import os

def send_email(subject, body, sender, recipients, password):
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = ', '.join(recipients)
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(sender, password)
       smtp_server.sendmail(sender, recipients, msg.as_string())

def html_parser(webContent):
    count = 0
    soup = BeautifulSoup(webContent, "html.parser")
    all_trs = soup.find_all("table")[0].find_all("tr")
    for tr in all_trs:
        if tr.find_previous(id="t"):
            count += 1
        jobPostings = tr.find_all("a", href=True)
        if count == 1 and (jobPostings != None):
            paragraphs = tr.find_all("p")
            if (paragraphs != None):
                return jobPostings, paragraphs

def html_parser_temp(webContent):
    found = False
    soup = BeautifulSoup(webContent, "html.parser")
    all_trs = soup.find_all("table")[0].find_all("tr")
    for tr in all_trs:
        if found:
            found = False
            jobPostings = tr.find_all("a", href=True)
            if (jobPostings != None):
                paragraphs = tr.find_all("p")
                if (paragraphs != None):
                    return jobPostings, paragraphs
        if (tr.text == "Technology"):
            found = True
    return None, None

def generate_email_body(jobPostings, paragraphs):
    email_body = ""
    if (jobPostings != None and paragraphs != None):
        for element in range(0,len(jobPostings)):
            jobPosting = jobPostings[element]["href"]
            paragraphTextArray = paragraphs[element+1].find_all(string=True)
            if (len(paragraphTextArray) >= 3):
                email_body += paragraphTextArray[0].strip() + ": " \
                            + jobPosting + "\n" \
                            + paragraphTextArray[1].strip() + "\n" \
                            + paragraphTextArray[2].strip() + "\n" \
                            + "\n"
    return email_body

def generate_tempJobPostings_file(jobPostings):
    if (jobPostings != None):
        f = open('tempJobPostings.txt', 'w')
        for jobPosting in jobPostings:
            f.write(str(jobPosting))
        f.close

def hashfile(file):
    BUF_SIZE = 65536
    sha256 = hashlib.sha256()
    with open(file, 'rb') as f:
        while True:
            data = f.read(BUF_SIZE)
            if not data:
                break
            sha256.update(data)
    return sha256.hexdigest()

def compare_jobPostings_files():
    f1_hash = hashfile('currentJobPostings.txt')
    f2_hash = hashfile('tempJobPostings.txt')
    if f1_hash == f2_hash:
        os.remove('tempJobPostings.txt')
        return False
    else:
        os.remove('currentJobPostings.txt')
        os.rename('tempJobPostings.txt','currentJobPostings.txt')
        return True

# Email
subject = "UCS Most Recent Technology Jobs"
sender = "YOUR_EMAIL_HERE"
recipients = ["LIST_OF_EMAIL_RECIPIENTS_HERE"]
password = "YOUR_SECRET_HERE"

# Website
url = 'https://ww2.nycourts.gov/job-postings-statewide-careers-22971'
response = urllib.request.urlopen(url)
webContent = response.read().decode('UTF-8')

# Compare job postings
jobPostings, paragraphs = html_parser_temp(webContent)
generate_tempJobPostings_file(jobPostings)
comparison = compare_jobPostings_files()

# Send email if job postings have been updated
if (jobPostings == None or paragraphs == None):
    send_email("ERROR! CHECK CODE!","",recipients, password)
else:
    if comparison:
        body = generate_email_body(jobPostings, paragraphs)
        send_email(subject, body, sender, recipients, password)

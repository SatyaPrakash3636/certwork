#!/usr/bin/env python2.7

from datetime import datetime
from OpenSSL import crypto
import os, shutil, os.path
from git import Repo
import glob
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import fileinput

target_dir = os.getcwd() + "/repodir"
pem_locations = target_dir + "/certificates/*/pem/*.pem"
git_url = "https://user:token@repoURL"
outfile = "expiry_details.html"

toemail = "test@mycomp.com"
def html_start(outfile):
    with open(outfile, 'w') as f4:
        f4.write('<!DOCTYPE html><html><head> <meta name="description" content="PEM Expiry Details"> <meta name="author" content="Satyaprakash Prasad"> </head>')
        f4.write('<style> h1 {text-align: center;} table { border-collapse: collapse; width: 100%; } th, td { border: 1px solid #ddd; text-align: left; padding: 8px; } tr:nth-child(even) { background-color: #F2F2F2; } th { background-color: #4CAF50; color: white; } </style>')
        f4.write('<body> <h1><u>PEM Expiry Details</u></h1>')
        f4.write('<table><tr><th>Environment</th><th>Region</th><th>Certificate Location in GIT</th><th>Common Name</th><th>Expiry (DD-MM-YYYY)</th><th>Days Remaining</th><th>Has Expired</th></tr>')

def html_content(outfile, env, state, certname, cn, exp_date, days_to_expire, expired):
    with open(outfile, 'a') as f4:
        #f4.write(f'<tr><td>{env}</td><td>{state}</td><td>{cn}</td><td>{exp_date}</td><td>{days_to_expire}</td><td>{expired}</td></tr>')
        f4.write('<tr><td>{0}</td><td>{1}</td><td>{2}</td><td>{3}</td><td>{4}</td><td>{5}</td><td>{6}</td></tr>'.format(env, state, certname, cn, exp_date, days_to_expire, expired))

def html_end(outfile):
    with open(outfile, 'a') as f4:
        f4.write('</table></body></html>')

def cloneRepo(target_dir, git_url):
    if os.path.isdir(target_dir):
        shutil.rmtree(target_dir)
        #print "removing {0}".format(target_dir)
    os.mkdir(target_dir)
    #print "dir created"
    Repo.clone_from(git_url, target_dir)


def get_details(outfile, pem_data, certFileName):
    cert = crypto.load_certificate(crypto.FILETYPE_PEM, pem_data)
    details = cert.get_subject()
    # country =details.C
    # locality =details.L
    state = details.ST
    # org = details.O
    # orgUnit = details.OU
    cn = details.CN
    #expiry = cert.get_notAfter()
    expiry = cert.get_notAfter().decode('utf-8')
    expired = cert.has_expired()
    expiry_time = datetime.strptime(expiry, '%Y%m%d%H%M%SZ')
    current_time = datetime.utcnow()
    days_to_expire = int((expiry_time - current_time).days)
    envDirLocIndex = len(os.getcwd().split("/")) + 2
    env = certFileName.split("/")[envDirLocIndex]
    #certLocIndex = envDirLocIndex + 2
    #certname = certFileName.split("/")[certLocIndex]
    certname = certFileName[len(os.getcwd()) + 8:]
    exp_date = str(expiry_time.day) + "-" + str(expiry_time.month) + "-" + str(expiry_time.year) + " " + str(expiry_time.hour) + ":" + str(expiry_time.minute) + " " + "UTC"
    #if days_to_expire >= 0 and days_to_expire < 15:
    if days_to_expire < 15:
        html_content(outfile, env, state, certname, cn, exp_date, days_to_expire, expired)

def send_email(toaddr, FileName):
    fromaddr = "EAI.Admin.ACN@noreply.com"
    msg = MIMEMultipart('alternative')
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "TIBCO SERVER CERTIFICATE EXPIRY REPORT"

    body = open(FileName).read()
    msg.attach(MIMEText(body, 'html'))

    server = smtplib.SMTP('smtp.server.com', 25)
    text = msg.as_string()
    server.sendmail(fromaddr, toaddr.split(','), text)
    server.quit()

cloneRepo(target_dir, git_url)
html_start(outfile)
for certFileName in glob.glob(pem_locations):
    if os.path.exists(certFileName):
        with open(certFileName, 'r') as f:
            pem_data = f.read()
            get_details(outfile, pem_data, certFileName)

html_end(outfile)
send_email(toemail, outfile)

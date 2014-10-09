"""An log class that writes a html file, and send result to mail.

Author : Sebastian Mariendal Kristensen
         Vejle Kommmune
         semkr@vejle.dk

Example:

>>> from Logthis import log
>>> mylog = log('newname') # Creates a new logfile in thisfolder/log/
                                    # logfile is namned 'newname'_year_month_date_time.html
#                   Sender                  subscriberlist                                                                          smtpadress          send omny mail at error
>>>mylog.InitMail('sender@domainname.com',['subscriber1@domainname.com','subscriber2@domainname.com','subscriber3@domainname.com'],'smtp.domainname.com',True)
>>>try:
>>>     # some kode
>>>     mylog.Writeln('This is what I am going to do') # write a line to log
>>>except:
>>>     mylog.Error('Error description') # write a error text to log

>>>mylog.Close() # close the file and send a mail to subscripters if InitMail is set.


"""

import sys, string, os, time, fileinput,smtplib, arcpy,  datetime,shutil
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from arcpy import da



class InitLog:
        def __init__(self, newname='Logthis', category=None,scriptversion = '1.0'):
            """log(name  as text , category as text, scriptversion as text)
                Creates a log object and a folder called 'LOG' in scriptfolder
                and a new open a textfile to start writing the logfile

                newname is a frieldly name of the script. The name is used in
                    the logfilename, mail subject text if mail is initialized,
                    and in the database if database is initialized.
                    Default value is 'test'

                category : The category of the script. If you have many scripts,
                    then use categorys to sort there logs in the database
                    default is None or ""

                scriptversion is to  set the version of your script, so you can tjek
                    if errors occoures after a new version.
                    max  length of 5 chars.
                    Default value is '1.0'"""
            self.Count = 0
            if not isinstance(category, type(None)):
                self.Category = str(category)
            else:
                self.Category = ''
            self.name = newname
            if len(self.Category)>0:
                self.ThislogName = self.Category + '_' + self.name
            else:
                 self.ThislogName = self.name
            self.ErrorCount = 0
            self.InfoCount=0
            self.references = 0
            self.open = 0
            self.StartTime = datetime.datetime.now()
            self.EndTime =None
            self.dato_tid =time.strftime("%Y%b%d_%H%M%S", time.localtime())
            self.ThisFolder =  os.getcwd()
            self.ScriptPath = __file__
            self.ScriptVersion = scriptversion
            self.DatabaseReady = False
            self.date_pretty = datetime.datetime.now().strftime("%d. %B %y")
            self.css =(
                '<style type="text/css">\n'
                'body {background: #fdfdfd;}\n'
                'table { width:70%; margin: auto; border-collapse:collapse;  }\n'
                'td { padding:8px; border-left:#999 1px solid; border-top:#999 1px solid; }\n'
                'th {  background: #222;  color: white;  padding:15px; border-left:#999 1px solid; border-top: none;}\n'
                'th,td:first-child { border-left: none;}\n'
                'th:first-child { border-radius: 10px 0 0 0;}\n'
                'th:last-child {border-radius: 0 10px 0 0;}\n'
                'th:only-child{ border-radius: 10px 10px 0 0;}\n'
                'tr:nth-child(even) { background: #A4D1FF;}\n'
                'tr:nth-child(odd) { background: #EAF4FF;}\n'
                'tfoot {   border-bottom-left-radius: 10px; border-bottom-right-radius: 10px;   display:block}\n'
                'tr.error { background: #FF6B6B; color:black;}\n'
                'h1 { color: #111; font-family: \'Open Sans Condensed\', sans-serif; font-size: 48px; font-weight: 700; line-height: 48x; margin: 0 0 0; padding: 20px 30px; text-align: center; text-transform: uppercase; }\n'
                'h2 { color: #111; font-family: \'Open Sans Condensed\', sans-serif; font-size: 30px; font-weight: 700; line-height: 30px; margin: 0 0 24px; padding: 0 30px; text-align: center; text-transform: uppercase; }\n'
                'p { color: #111; font-family: \'Open Sans\', sans-serif; font-size: 16px; line-height: 12px; margin: 0 0 12px; }\n'
                'a { color: #990000; text-decoration: none; }\n'
                'a:hover { text-decoration: underline }\n'
                'a.next {color: #990000; text-decoration: none; font-size: 12px; padding: 0 10px; position: relative; top: -10px; z-index: 100;}\n'
                'a.next:hover { text-decoration: underline; background: yellow; }\n'
                '.date { color: #111; display: block; font-family: \'Open Sans\', sans-serif; font-size: 16px; position: relative; text-align: center; z-index: 1; }\n'
                '.date::before { border-top: 1px solid #111; content: ""; position: absolute; top: 12px; left: 0; width: 100%; z-index: -1; }\n'
                '.category { color: #111; display: block; font-family: \'Open Sans\', sans-serif; font-size: 22px; padding-bottom: 38px; position: relative; text-align: center; z-index: 1; }\n'
                '.category:before { border-top: 1px solid #111; content: ""; position: absolute; top: 12px; left: 0; width: 100%; z-index: -1; }\n'
                '.date span,\n'
                '.category span { background: #fdfdfd; padding: 0 10px; }\n'
                '.line { border-top: 1px solid #111; display: block; margin-top: 60px; padding-top: 50px; position: relative; }\n'
                '.go-back { -moz-border-radius: 50%; -moz-transition: all 0.2s ease-in-out; -webkit-border-radius: 50%; -webkit-transition: all 0.2s ease-in-out; background: #111; border-radius: 50%; border: 10px solid #fdfdfd; color: #fff; display: block; font-family: \'Open Sans\', sans-serif; font-size: 14px; height: 80px; line-height: 80px; margin: -40px 0 0 -40px; position: absolute; bottom: 0px; left: 50%; text-align: center; text-transform: uppercase; width: 80px; }\n'
                '.go-back:hover { background: #990000; text-decoration: none; }\n'
                '.error {color:red;}\n'
                '.info {color : blue;}\n'
                '.credits { color: #111; display: block; font-family: \'Open Sans\', sans-serif; font-size: 8px; padding-bottom: 8px; position: relative; text-align: center; z-index: 1; }\n'
                '</style>\n'

                )
            self.dojo =('<link rel="stylesheet" href="http://ajax.googleapis.com/ajax/libs/dojo/1.7.2/dijit/themes/claro/claro.css" >\n'
                '<script src="http://ajax.googleapis.com/ajax/libs/dojo/1.7.2/dojo/dojo.js" data-dojo-config="async: true, parseOnLoad: true"></script>\n'
                '<script>\n'
                 '   require(["dojo/dom", "dijit/registry", "dijit/Dialog", "dojo/parser","dijit/form/Button", "dojo/domReady!"],\n'
                 '   function(dom,registry){\n'
                 '      dojo.ready(function(){\n'
                 '      });\n'
                 '});\n'
                'function showDialog(html) {\n'
                 "  dijit.byId('mydialog').set('title', html);\n"
                 "  dijit.byId('mydialog').set('href',html);\n"
                 "  dijit.byId('mydialog').show();\n"
                 '}\n'
                '</script>\n')
            self.FileName =''
            self.sender =''
            self.Receivers = []
            self.__alllogs_Layer__ ='All_Logs_Layer'
            self.SMTP =''
            self.mailready = False
            self.OnlyatError = False
            self.logfolder=os.path.join(self.ThisFolder, "log")
            if not os.path.exists(self.logfolder):
                os.makedirs(self.logfolder)

            self.FileName= os.path.join(self.logfolder, self.name + "_" + self.dato_tid + ".html"  )
            l = []
            if (os.path.isfile(self.FileName)):
                    self.fd2=open(self.FileName,'r')
                    #self.fd2.seek(524288,2)
                    self.fd2.seek(102400,2)
                    l = self.fd2.readlines()
                    self.fd2.close()
                    os.unlink(self.FileName)
            self.fd = open(self.FileName,'a')
            self.open = 1
            if len(l) >0:
                    self.fd.writelines(l)
            self.fd.write("<HTML>\n<TITLE>")
            self.fd.write("Log for " + self.name  +'</TITLE>\n')
            self.fd.write("<HEAD>\n")
            self.fd.write(self.css)
            self.fd.write("</HEAD>\n")
            self.fd.write("<BODY>\n")
            self.fd.write('<h2>Log for ' + self.name + '</h2>\n')
            if len(self.Category)>0:
                self.fd.write("<div class=\"category\"><span>Category : "+self.Category +"</span></div>")
            self.fd.write("<a name=\"TOP\"></a><div class=\"date\"><span>Started at : " + time.asctime(time.localtime()) +" </span></div>\n<p><a href=\"#ERROR"+str(self.ErrorCount)+"\" >Find error</a></p>\n")
            self.references += 1

        def InitMail(self, newSender, newReceivers, newSMTP, onlyaterror=False):
            """InitMail(newSender as text, newReceivers as list[ of text], newSMTP as text, onlyaterror as boolean)
                InitMail  send a mail with the log to a list of receivers.
                            if onlyaterror is True, then mails only is send at errors.


                newSender : a valid email in your domain, who will the send the mail
                                'sender@yourdomain.com'

                newReceivers : a list of valid emails, who wil receive the mail
                            ['receiver1@yourdomain.com','receiver2@yourdomain.com','receiver3@yourdomain.com']

                newSMTP : a valid SMTP server. 'SMTP.yourdomain.com'

                onlyaterror: sends only a mail if a error ocour. True|False
            """
            if isinstance(newSender, str) or isinstance(newSender, unicode):
                self.sender = newSender
            els
            if isinstance(newReceivers, list):
                self.Receivers = newReceivers
            else:
                arcpy.AddError('newReceivers is not a List')
            if isinstance(newSMTP, str):
                self.SMTP = newSMTP
            if isinstance(onlyaterror, bool):
                self.OnlyatError = onlyaterror
            if len(self.Receivers) > 0 and len(self.SMTP)>0 and len(self.sender) >0:
                self.mailready = True

        def InitDatabase(self,databasepath="",databasename=""):
            """InitDatabase(databasepath as text,databasename as text)
                Set up a log database, to collect logs from many scripts.
                if database not exist the script creates a new  ESRI Filegeodatabase
                    and creates a table called ALL_LOGS and table named 'catagory' + _ + 'newname'

                databasepath : The folder where the database is saved
                databasename : The name of the database + ".gdb"

                Table "ALL_LOGS" is the collecetion of all logs connectet to this database
                The table named after 'catagory' + _ + 'newname' is the collection of logs for this script."""

            if databasepath=="":
                databasepath=self.logfolder
            if databasename=="":
                databasename=self.name


            if databasename[-4:].lower() != '.gdb':
                databasename+='.gdb'
            if arcpy.Exists(os.path.join(databasepath,databasename)):
                self.Database = os.path.join(databasepath,databasename)
                if arcpy.Exists( os.path.join(self.Database,'ALL_LOGS')):
                    self.__alllogs__=os.path.join(self.Database,'ALL_LOGS')
                    arcpy.MakeTableView_management(self.__alllogs__,self.__alllogs_Layer__,"NAME = '" + self.name+"' AND CATEGORY = '"+ self.Category +"'")
                    rowcount= arcpy.GetCount_management(self.__alllogs_Layer__)
                    count =int(rowcount.getOutput(0))
                    ##print 'category', self.Category, 'Name', self.name, 'count', count
                    if count>0:
                        self.__Update_AllLogs__()
                        if arcpy.Exists((os.path.join(self.Database,self.ThislogName))):
                            self.__Thislog__ =os.path.join(self.Database,self.ThislogName)
                            self.DatabaseReady=True
                        else:
                            self.__CreateNewTable__(self.ThislogName)
                            self.DatabaseReady=True
                    else:
                        cursor = arcpy.da.InsertCursor(self.__alllogs__,["NAME","CATEGORY","VERSION","STARTED","LOG_NAME","SCRIPT_PATH"])
##                        row = cursor.newRow()
##                        row.setValue("NAME",self.name)
##                        row.setValue("CATEGORY",self.Category)
##                        row.setValue("VERSION",self.ScriptVersion)
##                        row.setValue("STARTED",self.StartTime)
##                        row.setValue("ENDED",self.EndTime)
##                        row.setValue("LOG_NAME",self.name + "_" + self.dato_tid + ".html")
##                        row.setValue("SCRIPT_PATH",self.ScriptPath)
##                        cursor.insertRow(row)
                        cursor.insertRow([self.name,self.Category,self.ScriptVersion, datetime.datetime.now(),self.ThislogName + "_" + self.dato_tid + ".html",self.ScriptPath])
                        del cursor
                        if arcpy.Exists((os.path.join(self.Database,self.ThislogName))):
                            self.__Thislog__ =os.path.join(self.Database,self.ThislogName)
                            self.DatabaseReady=True
                        else:
                            self.__CreateNewTable__(ThislogName)
                            self.DatabaseReady=True
                    del self.__alllogs_Layer__
                else:
                    arcpy.AddError(self.Database + " is not a valid Thislog database. \n Table 'ALL_LOGS' could not be found")
                    raise arcpy.ExecuteError
            else:
                self.__CreateNewDatabase__(databasepath,databasename)
                self.__CreateNewTable__(self.ThislogName)
                self.DatabaseReady=True


        def __CreateNewDatabase__(self,parth,name):
            if not arcpy.Exists(os.path.join(parth,name)):
                arcpy.CreateFileGDB_management(parth, name, "CURRENT")
                self.Database = os.path.join(parth,name)
                # Process: Create Domain
                arcpy.CreateDomain_management(self.Database, "ERROR", "ERROR or NOT", "SHORT", "CODED", "DEFAULT", "DEFAULT")
                # Process: Add Coded Value To Domain
                arcpy.AddCodedValueToDomain_management(self.Database, "ERROR", "0", "OK")
                # Process: Add Coded Value To Domain (2)
                arcpy.AddCodedValueToDomain_management(self.Database, "ERROR", "1", "ERROR")
                arcpy.CreateTable_management(self.Database, "ALL_LOGS", "", "")
                self.__alllogs__ =  os.path.join(self.Database, "ALL_LOGS")
                arcpy.AddField_management(self.__alllogs__, "NAME", "TEXT", "", "", "100", "Name", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "CATEGORY", "TEXT", "", "", "20", "Category", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "VERSION", "TEXT", "", "", "5", "Version", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "STARTED", "DATE", "", "", "", "Script start", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "ENDED", "DATE", "", "", "", "Script end", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "RESULT", "SHORT", "", "", "", "Result", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AssignDefaultToField_management(self.__alllogs__,"RESULT", 1)
                arcpy.AssignDomainToField_management(self.__alllogs__,"RESULT","ERROR")
                arcpy.AddField_management(self.__alllogs__, "LOG_BINARY", "BLOB", "", "", "", "Log binany", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "LOG_NAME", "TEXT", "", "", "100", "Log", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__alllogs__, "SCRIPT_PATH", "TEXT", "", "", "255",  "Script path", "NULLABLE", "NON_REQUIRED", "")
                cursor =arcpy.da.InsertCursor(self.__alllogs__,["NAME","CATEGORY","VERSION","STARTED","LOG_NAME","SCRIPT_PATH"])
##                row = cursor.newRow()
##                row.setValue("NAME",self.name)
##                row.setValue("CATEGORY",self.Category)
##                row.setValue("VERSION",self.ScriptVersion)
##                row.setValue("STARTED",self.StartTime)
##
##                row.setValue("LOG_NAME",self.name + "_" + self.dato_tid + ".html")
##                row.setValue("SCRIPT_PATH",self.ScriptPath)
##                cursor.insertRow(row)
                cursor.insertRow([self.name,self.Category,self.ScriptVersion, datetime.datetime.now(),self.name + "_" + self.dato_tid + ".html",self.ScriptPath])
                del cursor

        def __CreateNewTable__(self, name ):
            if not arcpy.Exists(os.path.join(self.Database, name)):
                name = arcpy.ValidateTableName(name,self.Database)
                arcpy.CreateTable_management(self.Database, name, "", "")
                self.__Thislog__=os.path.join(self.Database, name)
                arcpy.AddField_management(self.__Thislog__, "NAME", "TEXT", "", "", "100", "Name", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "CATEGORY", "TEXT", "", "", "20", "Category", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "VERSION", "TEXT", "", "", "5", "Version", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "STARTED", "DATE", "", "", "", "Script start", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "ENDED", "DATE", "", "", "", "Script end", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "RESULT", "SHORT", "", "", "", "Result", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AssignDefaultToField_management(self.__Thislog__,"RESULT", 1)
                arcpy.AssignDomainToField_management(self.__Thislog__,"RESULT","ERROR")
                arcpy.AddField_management(self.__Thislog__, "LOG_BINARY", "BLOB", "", "", "", "Log binany", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "LOG_NAME", "TEXT", "", "", "100", "Log", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AddField_management(self.__Thislog__, "COUNT", "LONG", "", "", "", "Count", "NULLABLE", "NON_REQUIRED", "")
                arcpy.AssignDefaultToField_management(self.__Thislog__,"COUNT", 0)


        def __Update_AllLogs__(self,binary = None):
##            print "binary",type(binary), binary
##            try:
                rows=arcpy.da.UpdateCursor(self.__alllogs__,["STARTED","ENDED","RESULT","LOG_BINARY","LOG_NAME","SCRIPT_PATH"],"NAME = '" + self.name + "' AND CATEGORY = '" + self.Category + "'",)
                for row in rows:


                    if self.ErrorCount > 0:
                        row[2]=1
                    else:
                        row[2]=0
                    row[0]=self.StartTime
                    row[1]=self.EndTime
                    row[3]=binary
                    row[4]=self.name + "_" + self.dato_tid + ".html"
                    row[5]=self.ScriptPath

    ##                     row.setValue("RESULT",1)
    ##                else:
    ##                    row.setValue("RESULT",0)
    ##                row.setValue("STARTED",self.StartTime)
    ##                row.setValue("ENDED",self.EndTime)
    ##                row.setValue("LOG_BINARY", "1")
    ##                row.setValue("LOG_NAME", self.name + "_" + self.dato_tid + ".html"  )
    ##                row.setValue("SCRIPT_PATH",self.ScriptPath)

                    #print"ALL_ROWS is updatet"
                    rows.updateRow(row)
                    del row
##            except arcpy.ExecuteError, e:
##                arcpy.AddError(e)
##            except RuntimeError, e:
##                arcpy.AddError(e)
##            finally:
                del rows

        def __Update_Thislog__(self,binary = None):
            try:
                cursor = arcpy.da.InsertCursor(self.__Thislog__,["NAME","CATEGORY","VERSION","STARTED","ENDED","RESULT","LOG_BINARY","LOG_NAME","COUNT"])
                fejl= 0
                if self.ErrorCount > 0:
                    fejl = 1
##                row = cursor.newRow()
##                row.setValue("NAME",self.name)
##                row.setValue("CATEGORY",self.Category)
##                row.setValue("VERSION",self.ScriptVersion)
##                row.setValue("STARTED",self.StartTime)
##                row.setValue("ENDED",self.EndTime)
##                row.setValue("RESULT", fejl)
##                row.setValue("LOG_BINARY", "2")
##                row.setValue("LOG_NAME",self.name + "_" + self.dato_tid + ".html")
##                row.setValue("COUNT",self.Count)
##                cursor.insertRow(row)
                cursor.insertRow([self.name,self.Category,self.ScriptVersion, self.StartTime,self.EndTime,fejl,binary,self.name + "_" + self.dato_tid + ".html",self.Count])
                print"Thislog is updatet"

            except arcpy.ExecuteError, e:
                    arcpy.AddError(e)
            except RuntimeError, e:
                    arcpy.AddError(e)
            finally:
                 del cursor

        def  __table2dojodrid__(self, tablename):
            structure = []
            fields=arcpy.ListFields(os.path.join(self.Database, tablename))
            for field in fields:
                length = 20
                if field.type == 'String':
                    length = field.length
                elif field.type == 'Date':
                    length=80

                if field.name not in ['LOG_BINARY','LOG_NAME']:
                    info ={}
                    info['name']=field.aliasName
                    info['field']=field.name
                    info['width'] =str(length) + 'px'
                    structure.append(info)
            del(fields)
            return json.dumps(structure)

        def Database2HMTL(self,OutputFolder):
            """Database2HMTL(OutputFolder as text):
                Database2HTML creates a  web report for all the logs in the
                 database.

                if mail is initialized , then a mail will be send to the
                recievers . If a script have a error it will be listet in the
                mail report.

                 "OutputFolder" : The output folder have to be a valid path, to
                 a virtuel folder on a webserver. Be shure that the script have
                  write permision to the folder.
            """
            if len(OutputFolder)==0 :
                OutputFolder =self.ThisFolder
            if self.DatabaseReady == True:
                if os.path.exists(OutputFolder):
                        shutil.rmtree(OutputFolder) # delete folder and all files
                        time.sleep(0.05) # wait 50 msec
                os.makedirs(OutputFolder) # creates the folder agian
                arcpy.env.workspace = self.Database
                for table in arcpy.ListTables():
                    ##    try:
                    filename = "index.html"
                    if table <> "ALL_LOGS":
                        filename = table + ".html"
                        nameList=table.split('_', 1 )
                        if len(nameList)>1:
                            tname= nameList[1]
                            tcategory =nameList[0]
                        else:
                            tname= table
                            tcategory=''
                    else:
                        tname= table
                        tcategory=''
                    fd = open(os.path.join(OutputFolder,filename),'a')
                    fd.write("<HTML>\n<TITLE>")
                    fd.write("Log for " + table  +'</TITLE>\n')
                    fd.write("<HEAD>\n")
                    fd.write(self.css)
                    fd.write(self.dojo)
                    fd.write("</HEAD>\n")
                    fd.write('<BODY class="claro">\n')
                    fd.write('<h2>Logs for ' + tname + '</h2>\n')
                    if len(tcategory)>0:
                        fd.write("<div class=\"category\"><span>Category : "+tcategory +"</span></div>\n")
                    fd.write('<date class="date"><span>' +self.date_pretty+'</span></date>')
                    fields = arcpy.ListFields(table)
                    fd.write('<br><br><TABLE>\n<THEAD>')

                    fd.write('<tr>')
                    fieldnames = []
                    for field in fields:
                        if field.name not in ["LOG_BINARY", "OBJECTID"]:
                            fieldnames.append(field.name)
                            fd.write('<th> ' + field.aliasName + '</th>')
                    if table =="ALL_LOGS":
                        fd.write('<th> ' + 'Historic logs' + '</t>')
                    fd.write("</tr></THEAD>\n<TBODY>\n<div id=\"mydialog\" data-dojo-type=\"dijit.Dialog\" style='width:90%;height:80%;' ></div>\n")
                    Tempcursor = arcpy.da.SearchCursor(table,["OBJECTID","LOG_BINARY","LOG_NAME"])
                    for row in Tempcursor:
                       binary = row[1]
                       if isinstance(binary, memoryview):
                            if len(binary)>0:
                                 open(OutputFolder + os.sep + row[2], 'wb').write(binary.tobytes())
                       del row,binary
                    del  Tempcursor
                    cursor= arcpy.SearchCursor(table,sort_fields="STARTED D")
                    #print table
                    #print "fields;", len(fields)
                    for row in cursor:
                        sName = row.getValue('NAME')
                        sCategory =row.getValue("CATEGORY")
                        if len (sCategory)>0:
                            tablename =sCategory +'_'+sName
                        else:
                            tablename = sName
                        tjeckError =row.getValue('RESULT')
                        if tjeckError== 1:
                            fd.write('<tr class="error">\n')
                            if table == "ALL_LOGS" and tablename<>self.ThislogName:
                                self.Error('Error occurred whith '+ tablename)
                        else:
                            fd.write('<tr>\n')
                        for name in fieldnames:
                            value = row.getValue(name)
                            tekst = ""

                            if isinstance(value,memoryview):
                                tekst = str(value.tobytes())
                            elif isinstance(value,datetime.date):
                                tekst=value.strftime("%Y-%m-%d %H:%M:%S")
                            elif isinstance(value,type(None)):
                                tekst=''
                            else:
                                tekst=str(value)
                            if name=='RESULT':
                                if tjeckError==0:
                                    tekst='OK'
                                else:
                                    tekst='ERROR'
                            if name == 'LOG_NAME':
                                tekst="<button  data-dojo-type=\"dijit.form.Button\" onclick='showDialog(\""+value+"\")'>Show log</button>"

                            fd.write('<td>' + tekst + '</td>')
                        if table =="ALL_LOGS":
                            fd.write('<td><button data-dojo-type="dijit.form.Button" type="button">view historic logs\n <script type="dojo/connect" data-dojo-event="onClick">\n  window.location = "' +tablename+ '.html";\n   </script>\n </button></td>')

                        fd.write('</tr>\n')
                    fd.write('</TBODY>\n</TABLE>\n')
                    if table<>"ALL_LOGS":
                        fd.write('<div class="line"><a class="go-back" href="index.html">Go Back</a></div>\n')
                    fd.write('<p class="credits">&copy;Logthis - Municipality of Vejle - Denmark</p>\n')
                    fd.write('</BODY>\n</HTML>')
                    fd.close()
                    del(cursor,fields,fd)
                ##    except:
                ##        print 'Der er sket en fejl'
                ##    finally:
                ##        del(cursor,fields,fd)
            else:
                arcpy.AddError('Database is not initialiced \n Use InitDatabase() before Database2HTML()')
                raise arcpy.ExecuteError


        def SetCount(count):
            """SetCount(int)
                Set the count value in Log table
            """
            if isinstance(count, int):
                self.Count= count
            else:
                arcpy.AddError('count is not a int')
                raise arcpy.ExecuteError


        def DeleteLog(self, onlylogfiles=False):
            """DeleteLogs(onlylogfiles as boolean)
                Delete all logs from database, by name and category
                Delete the folder and logs in 'LOG' folder
                if onlylogfiles is set to True, then logs in database is not deleted
            """
            self.fd.close()
            self.open = 0
            if not onlylogfiles:
                if self.DatabaseReady:
                    with arcpy.da.UpdateCursor(self.__alllogs__,"NAME == '" + self.name+"' AND CATEGORY == '"+ self.Category +"'") as cursor:
                        for row in cursor:
                            cursor.deleteRow()
                    del cursor
                    if arcpy.Exists(self.__Thislog__):
                        arcpy.Delete_management(self.__Thislog__)
            if os.path.exists(self.logfolder):
                shutil.rmtree(self.logfolder)

        def DeleteDBLogsByDate(self, date):
            """DeleteDBLogsByDate(date as datetime)
                Deletes all logs in database older than 'date'.
                Use this function to clean up the database for old logs.
            """
            if isinstance(date, (datetime.date,datetime.datetime)):
                if self.DatabaseReady == True:
                    arcpy.env.workspace = self.Database
                    for table in arcpy.ListTables():
                        updateCursor = arcpy.UpdateCursor(table, "STARTED < date '"+ date.strptime("%Y-%m-%d %H:%M:%s") + "'" )
                        for row in updateCursor:
                            updateCursor.deleteRow()
                        del updateCursor

                else:
                    arcpy.AddError('Database is not initialized. Run'
                    ' InitDatabase() before this function.')
                    raise


            else:
                arcpy.AddError('date is not a valid datetime object')
                raise

        def Close(self):
                """Close()
                    Close the log objct, save the logfile
                    if mail is initiated, a mail will be send to the recievers.
                    if database is initiated the log wil be saved in the database"""
                self.EndTime = datetime.datetime.now()
                self.fd.write("<a nane=\"ERROR" + str(self.ErrorCount) + "\"></a><div class=\"date\"><span>Ended at : "+time.asctime(time.localtime())+ "</span></div><BR>\n")
                self.fd.write("<a class=\"next\" href=\"#TOP\">To Top</a><br>\n")
                self.fd.write('<p class="credits">&copy;Logthis - Municipality of Vejle - Denmark</p>\n</BODY>\n</HTML>')
                self.fd.close()
                self.open = 0
                self.references -= 1
                temp=open(self.FileName, "r")
                logtekst=temp.read().rstrip('\n')
                binary =logtekst # memoryview(logtekst)
                temp.close()

                if self.mailready == True:
                    self.body = open(self.FileName).read().replace('\n','')

                    self.msg = MIMEMultipart()
                    if self.ErrorCount > 0:
                        self.subject = "ERROR : " + self.name
                    else:
                        self.subject = self.name + " OK"
                    self.msg['From'] = self.sender
                    self.msg['To'] = ','.join(self.Receivers)
                    self.msg['Subject'] = self.subject
                    self.msg.attach(MIMEText(self.body, 'html'))
                    self.message=self.msg.as_string()
                    if (self.ErrorCount > 0 and self.OnlyatError) or not self.OnlyatError:
                        self.mail = smtplib.SMTP(self.SMTP)
                        self.mail.sendmail(self.sender,self.Receivers, self.message)
                        self.mail.quit()
                if self.DatabaseReady == True:
                   self.__Update_AllLogs__(binary)
                   self.__Update_Thislog__(binary)



        def Writeln(self,line):
                """Writeln(line as text)
                   Writeln writes a line of text to the log
                   """
                print line
                line ='<p>' + line +'</p>\n'
                self.fd.write(line)
                self.fd.flush()

        def Write(self,line):
                """Writeln(line as text)
                   Writeln write text to the log
                   Clean text, so good to use to write HTTML"""
                print line
                self.fd.write(line)
                self.fd.flush()

        def Info(self, line):
                """Info(line as text)
                Info writes a info message to the log.
                a Infomessage is not a error, but a information you like to make special"""
                print line
                self.fd.write('<a name="INFO' + str(self.InfoCount) + '"></a><p class="info">' + line + '</p>\n')
                self.InfoCount += 1
                self.fd.write( "<a class=\"next\" href=\"#INFO" + str(self.InfoCount) + "\">Find next info</a><br>\n" )
                self.fd.flush()

        def Error(self,line):
                """Error(line as text)
                    Error writes a errormessage to the log
                    if mail is initiated a mail is send to recievers whith "ERROR" in headertext"""
                print line
                self.fd.write('<a name="ERROR' + str(self.ErrorCount) + '"></a><p class="error">' + line + '</p>\n')
                self.ErrorCount += 1
                self.fd.write( "<a class=\"next\" href=\"#ERROR" + str(self.ErrorCount) + "\">Find next error</a><br>\n" )
                self.fd.flush()

        def Copy_file(self,otherfile):
                """Copy_file(otherfile as text)
                   Copy_file copy the logfile used in this session to a new file
                   otherfile : a vallid path and filename to the newfile."""
                if (os.path.isfile(otherfile)):
                        self.fd.close()
                        self.fd2=open(otherfile,'r')
                        l = self.fd2.readlines()
                        self.fd2.close()
                        self.fd = open(self.FileName,'a')
                        if len(l) >0:
                                for ll in l:
                                        self.fd.write(ll+"<BR>\n'")
                                        print ll + '\n'

        def __del__(self):
                if (self.open == 1) and (self.references < 1):
                        self.fd.close()
                        self.open = 0
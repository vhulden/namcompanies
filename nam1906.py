# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 12:43:30 2016

@author: Vilja Hulden

This script takes the OCR'd list of NAM companies (1913 and 1906 American 
Trade Indexes, alphabetical portion) and converts it into a csv table with 
company, street, city, state. It does decently but requires manual corrections
afterward. 

It also creates a separate list of other names the companies indicate themselves
to use or have used, e.g. successors, "also doing business as" and so on. This is saved separately.

One file at a time.
"""

import re

filesdir = "employerorglists/"

writedir = "employerorglists/"

#readfile = "test.txt"
readfile = "nam_alphabetical_1906_ati.txt"
statesfile = "states.csv"
companiesfilename = 'companies1906.txt'
successorsfilename = 'otherconames1906.txt'

with open(statesfile) as f0:
    states = f0.read().decode("utf-8-sig").encode("utf-8")

statelist = []
costates = []

statelines = states.splitlines()

for state in statelines:
    st = state.split(',')
    statelist.append(st)

stnotfound = []
companies = []
companiestxt = ''
othernames = []
pattern = '(^.*?,.*?[.;](\s*[A-Z]\.)*)' #'(.*?),(.*?\.(?:\s*[A-Z]\.)*)'

with open(filesdir+readfile) as f:
    cofile = f.read().decode("utf-8-sig").encode("utf-8")

#This attempts to preprocess the whole text to get rid of some junk and normalize
#things that confuse the script or cause things to be chunked wrong (e.g. the lack
#of state in all New York City addresses)

print "Making basic substitutions..."
cofile = re.sub('\r','\n',cofile)
cofile = re.sub('\n\n','\n',cofile)
cofile = re.sub('Please mention.*\n','',cofile)
cofile = re.sub('.*to manufacturers whose names.*\n','',cofile)
cofile = re.sub('Digitized.*\n','',cofile)
cofile = re.sub('^.*AMERICAN TRADE INDEX.*$','',cofile)
cofile = re.sub('-\s*\n','',cofile)
cofile = re.sub(',\s*\n',', ',cofile)
cofile = re.sub(';\s*\n','; ',cofile)
cofile = re.sub(':\s*\n',': ',cofile)
cofile = re.sub('\n\s*\.',' ',cofile)
cofile = re.sub('\n\s*([a-z0-9])',' \\1',cofile)
cofile = re.sub('111\.',' Ill.',cofile)
cofile = re.sub('I11\.',' Ill.',cofile)
cofile = re.sub('l11\.',' Ill.',cofile)
cofile = re.sub('St\.','St',cofile) #because period is used for matching; but not Saint b/c co names might get changed ("st. louis brewing")
cofile = re.sub('Mt\.','Mount',cofile)
cofile = re.sub('l11\.',' Ill.',cofile)
cofile = re.sub(',\s*Inc\.',' Inc',cofile)
cofile = re.sub(',\s*Ltd\.',' Ltd',cofile)
cofile = re.sub(',\s*Co\.',' Company',cofile)
cofile = re.sub('street\.','street',cofile)
cofile = re.sub('[Pp]rop\.','Proprietor',cofile)
cofile = re.sub('(([Ss]treet)|([Ss]treets)|(Broadway)|([Ll]ane)|([Aa]venue)|([Pp]lace)),\s*(New York)',' \\1, New York, NY',cofile)
colist = cofile.split('\n')

 
print "Processing companies..."
counter = 0
for line in colist:
    if counter % 10 == 0:
        print ".",
    counter +=1
    m = ""
    #this bit tries to deal with company names like 
    #"Dewey, Cheetham, Howe & Co." - i.e. names that have commas in them
    #it is restricted to the first 65 characters of the line because
    # otherwise it matches " & Co." if it's in "Foreign agents..." or some
    # such and then all commas needed for city and state chunking disappear.
    listnamepattern = "(^.{0,65})((?:&\s*Co\.)|(?:&\s*Sons)|(?:and\s*Sons)|(?:Company))(.*)"  
    m = re.search(listnamepattern,line)
    if m:
        linept1 = m.group(1)
        linept1nocomma = re.sub(",","",linept1)
        linept2 = m.group(2)
        linept3 = m.group(3)
        line = linept1nocomma + linept2 +linept3
    
    #clean so they don't hang around for the next co erroenously   
    coname = ""
    coaddress = ""
    costate = ""
    costreet = ""
    cocity = ""
    m = ""
    m2 = ""
    m3 = ""
    m = re.search(pattern,line)
    if m:
        colinedraft = m.group(0).split(',')
        costate = colinedraft[-1]
        if len(colinedraft) > 3:
            cocity = colinedraft[-2]
            costreet = colinedraft[-3]
            coname = colinedraft[:-3]
            coname = ' '.join(coname)
        else:
            cocity = colinedraft[-2]
            coname = colinedraft[0]
        for state in statelist:
            for abbr in state:
                strippattern = re.compile('\s+|\.')
                if re.sub(strippattern,'',costate) == re.sub(strippattern,'',abbr):
                    costate = state[0].strip()

    
    if len(costate) != 2:
        costates.append(coname + ' ' + costate)
    
    #catch other names of companies (like "Succeeded by" or "Formerly")
    #save in a separate list
    
    othername = re.search('(.*?)\((.*?)\)',coname)
    if othername:
        coname = othername.group(1).strip() 
        othernameline = coname + " # " + othername.group(2).strip()
        othernames.append(othernameline)
     
    colist = [coname,costreet,cocity,costate]
    companies.append(colist)
    

print "\nWriting files..."

for colist in companies:
    if ''.join(colist):
        companiestxt += ', '.join(colist) + '\n'

othernametxt = '\n'.join(othernames)

with open(writedir+companiesfilename,'w') as f:
    f.write(companiestxt)
    
with open(writedir+successorsfilename,'w') as f:
    f.write(othernametxt)
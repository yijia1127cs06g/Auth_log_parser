import time
import argparse
import re
from prettytable import PrettyTable



dateFormat = '%Y-%b-%d-%H:%M:%S'


def startup():
    argparser = argparse.ArgumentParser()
    argparser.add_argument("filename", help="Log file path.")
    argparser.add_argument("-u",
            help = "Summary failed login log and sort log by user", action = "store_true")
    argparser.add_argument("-after",  help = "Filter log after date. format YYYY-MM-DD-HH:MM:SS")
    argparser.add_argument("-before",  help = "Filter log before date. format YYY-MM-DD-HH:MM:SS")
    argparser.add_argument("-n",  help = "Show only the user of most N-th times",
            type = int)
    argparser.add_argument("-t",
            help = "Show only the user of attacking equal or more than T times",
            type = int, default = 0)
    argparser.add_argument("-r",
            help = "Sort in reverse order", action = "store_true")
    return argparser.parse_args()
   
def getUser(line):
    try:
        for element in line[3:]:
            if 'sshd' in element:
                Start = line.index(element)
                break
        else:
            raise ValueError
        End = line.index('from')
        if line[End+1] == 'from':
            End -= 1
    except ValueError:
        print("In log file: log format error: "+ ' '.join(line))
        exit()
    
    user = line[End-1]
    userType = ' '.join(line[Start+1:End-1])
    return [user, userType]

def getDate(line):
    # abc = time.strptime('-'.join(line[:4]), dateFormat)
    # print(abc)
    try:
        date = time.strptime('-'.join(line[0:4]), dateFormat)
        # print(date)
        return date
    except ValueError:
        try:
            date = time.strptime('2018-'+'-'.join(line[:3]), dateFormat)
            # print(date)
            return date
        except ValueError:
            print("In log file: Time format error: "+ ' '.join(line))


def parseLog(log):
    line = log.split()
    date = getDate(line)
    if getUser(line)[1] == 'Invalid user':
        return [date, getUser(line)[0]]


def cutByDate(record, after, before):
    copy = record.copy()
    copy.sort()
    
    if after == None:
        startDate = time.strptime('1900-Jan-1-0:0:0', dateFormat)
    else:
        try:
            startDate = time.strptime(after, '%Y-%m-%d-%H:%M:%S')
        except:
            print("Time format error: " + after)
            print("Format should be YYYY-MM-DD-HH:MM:SS")
            print("E.g. 2018-01-01-00:00:00")
            exit()
    
    if before == None:
        endDate = time.localtime(time.time())
    else:
        try:
            endDate = time.strptime(before, '%Y-%m-%d-%H:%M:%S')
        except:
            print("Time format error: " + before)
            print("Format should be YYYY-MM-DD-HH:MM:SS")
            print("E.g. 2018-01-01-00:00:00")

    for element in copy:
        if element[0] < startDate:
            continue
        start = copy.index(element)
        break
    else:
        print("There is no data after ")
        return []

    for element in copy[::-1]:
        if element[0] > endDate:
            continue
        end = copy.index(element)
        break
    else:
        print("There is no data before")
        return []
    
    return copy[start:end+1]


def countFrequency(record):
    countList = {}
    for element in record:
        key = element[1]
        if key in countList:
            countList[key] += 1
        else:
            countList[key] = 1

    return countList

def timeFilter(countList, lower):
    deleteList = []
    for key in countList:
        value = countList[key]
        if value<lower:
            deleteList.append(key)

    return deleteList

def makeTable(rows, count):
    x = PrettyTable()
    x.field_names = ['user','count']
    for i in range(count):
        rows[i].reverse()
        x.add_row(rows[i])
    print(x)

def Main():
    args = startup()

    
    with open(args.filename, 'r') as myfile:
        logFile = myfile.read()
        logFile = logFile.strip('\n')
        logList = re.split(r'\n', logFile)
    
    record = []
    for log in logList:
        userRecord = parseLog(log)
        if userRecord != None:
            record.append(parseLog(log))

    
    # deal with -after, -before
    record = cutByDate(record, args.after, args.before)
    # count each user's login times
    countList = countFrequency(record)
    # deal with -n: at most time and -t: at least time
    deleteList = timeFilter(countList,  args.t)
    for key in deleteList:
        del countList[key]


    # deal with -u: sort by user and -n
    rows = []
    x = 0
    if args.u == True:
        for key in countList:
            rows.append([key,countList[key]])
        rows.sort()
        rows.reverse()
    else:
        for key in countList:
            rows.append([countList[key], key])
        rows.sort()
    if args.r == False:
        rows.reverse()
    # if -u then each row data is reverse. so have to reverse back
    if args.u == True:
        for row in rows:
            row.reverse()
    # deal with -n: add n rows 
    if args.n == None or args.n > len(rows):
        rowCount = len(rows)
    else:
        rowCount = args.n

    makeTable(rows, rowCount)


if __name__ == '__main__':
    Main()

def dictToTable(dictionary):
    print "<table cellpadding=10>"
    for d in dictionary:
        print "<tr>"
        print "<td>"
        print d
        print "</td>"
        print "<td>"
        print dictionary[d]
        print "</td>"
        print "</tr>"
    print "</table>"

def webMenu(dictionary):
    print "<table cellpadding=5>"
    print "<tr>"
    for d in dictionary:
        
        print "<td>"
        print "<a href=\""
        print dictionary[d]
        print "\">"
        print d
        print "</a>"
        print "</td>"

    print "</tr>"
    print "</table>"

def title():
    print "<b>Teledrill Decoder Web Interface Alpha</b><br><br>"
        

def header():
    print "Content-type: text/html\n"

    

        

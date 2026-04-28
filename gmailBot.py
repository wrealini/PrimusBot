import getpass, imaplib2

EMAIL = 'primusdiscordbot@gmail.com'
SERVER = 'imap.gmail.com'

def cb(cb_arg_list):
    response, cb_arg, error = cb_arg_list
    typ, data = response
    if not data:
        return
    for field in data:
        if type(field) is not tuple:
            continue
        messagebody = str(field[1])
        messagebody = messagebody.split('\\r\\n')
        messagebody = messagebody[-2]
        print(messagebody)

def runGmailBot():
    f = open('gmailPassword.txt')
    gmailPassword = f.read()
    f.close()
    M = imaplib2.IMAP4_SSL(SERVER)
    M.LOGIN(EMAIL, gmailPassword)
    M.SELECT(readonly=True)
    while True:
        print("Going into idle...")
        M.idle(timeout=None)
        typ, data = M.SEARCH(None, 'ALL')
        M.FETCH(data[0].split()[-1], '(RFC822)', callback=cb)
    M.CLOSE()
    M.LOGOUT()
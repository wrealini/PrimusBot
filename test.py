# import email
# import imaplib

# EMAIL = 'primusdiscordbot@gmail.com'
# SERVER = 'imap.gmail.com'

# f = open('gmailPassword.txt')
# gmailPassword = f.read()
# f.close()
# print(gmailPassword)

# mail = imaplib.IMAP4_SSL(SERVER)
# mail.login(EMAIL, gmailPassword)
# mail.select('inbox')
# status, data = mail.search(None, 'ALL')
# mail_ids = []
# for block in data:
#     mail_ids += block.split()

# for i in mail_ids:
#     status, data = mail.fetch(i, '(RFC822)')
#     for response_part in data:
#         if isinstance(response_part, tuple):
#             message = email.message_from_bytes(response_part[1])
#             mail_from = message['from']
#             mail_subject = message['subject']
#             if message.is_multipart():
#                 mail_content = ''

#                 for part in message.get_payload():
#                     if part.get_content_type() == 'text/plain':
#                         mail_content += part.get_payload()
#             else:
#                 mail_content = message.get_payload()
#             print(f'From: {mail_from}')
#             print(f'Subject: {mail_subject}')
#             print(f'Content: {mail_content}')

EMAIL = 'primusdiscordbot@gmail.com'
SERVER = 'imap.gmail.com'

f = open('gmailPassword.txt')
gmailPassword = f.read()
f.close()
print(gmailPassword)

def cb(cb_arg_list):
    response, cb_arg, error = cb_arg_list
    typ, data = response
    if not data:
        return
    for field in data:
        if type(field) is not tuple:
            continue
        print('Message %s:\n%s\n'
            % (field[0].split()[0], field[1]))

import getpass, imaplib2
M = imaplib2.IMAP4_SSL(SERVER)
# M.LOGIN(getpass.getuser(), getpass.getpass())
M.LOGIN(EMAIL, gmailPassword)
M.SELECT(readonly=True)
typ, data = M.SEARCH(None, 'ALL')
for num in data[0].split():
    M.FETCH(num, '(RFC822)', callback=cb)
M.CLOSE()
M.LOGOUT()
import imaplib, os,platform

from_server = {}

to_server = {}

arq = open('cfg.txt','r').read()

exec(arq)

def clear():
   if platform.system() == 'Windows':
      os.system('cls')
   else:
      os.system('clear')

def get_mailbox(From,To):
    for x in From.list()[1]:
        name = x.decode().split('"."')[1].strip()
        if from_server['box_names'] == []:
            from_server['box_names'].append(name)
            to_server['box_names']=[]
            to_server['box_names'].append(name)
            To.create(name)

def connect_server(server):
    conn = imaplib.IMAP4_SSL(server['server']) 
    conn.login(server['username'], server['password'])
    print('Logged into mail server {}'.format(server['server']))
    return conn

def disconnect_server(server_conn):
    out = server_conn.logout()

if __name__ == '__main__':
    From = connect_server(from_server)
    To = connect_server(to_server)

    get_mailbox(From, To)

    for idx,box in enumerate(from_server['box_names']):
        box_select = From.select(box, readonly = False)  #open box which will have its contents copied
        #box_select = From.select()  #open box which will have its contents copied
        print(f'Fetching messages from \'{box}\'...')
        resp, items = From.search(None, 'ALL')
        msg_nums = items[0].split()
        print(f'{len(msg_nums)} messages to archive\n')

        length_data = len(msg_nums)

        char_='='

        for idy,msg_num in enumerate(msg_nums):
            idy_ = idy +1
            buffer = int((idy_/length_data)*100)*char_
            print('['+buffer.ljust(100)+']',f' {int((idy_/length_data)*100)}%')
            resp, data = From.fetch(msg_num, "(FLAGS INTERNALDATE BODY.PEEK[])") # get email
            message = data[0][1] 
            flags = imaplib.ParseFlags(data[0][0]) # get flags
            flag_str = " ".join([x.decode('utf-8') for x in flags])
            date = imaplib.Time2Internaldate(imaplib.Internaldate2tuple(data[0][0])) #get date
            copy_result = To.append(to_server['box_names'][idx], flag_str, date, message) # copy to archive

            if copy_result[0] == 'OK':
                #del_msg = From.store(msg_num, '+FLAGS', '\\Seen') # mark for deletion
                del_msg = From.store(msg_num, '+FLAGS', '\\Seen')

            clear()

        #ex = From.expunge() # delete marked
        ex = From.expunge()
        print('expunge status: {}'.format(ex[0]))
        #if not ex[1][0]: # result can be ['OK', [None]] if no messages need to be deleted
        if not ex[1][0]:
            print('expunge count: 0')
        else:
            print(f'expunge count: {len(ex[1])}')

        disconnect_server(From)
        disconnect_server(To)

input('Press any key to exit!')
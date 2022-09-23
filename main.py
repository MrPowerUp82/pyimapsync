import imaplib, os,platform, sys

from_server = {}

to_server = {}

point_msg = None

if sys.argv:
    try:
        sys.argv[1] = int(sys.argv[1])
        assert type(sys.argv[1]) == int, u'Erro, formato de idx inválido!'
        point_msg = sys.argv[1]
    except:
        point_msg = None

arq = open('cfg.txt','r').read()

exec(arq)

def clear():
   if platform.system() == 'Windows':
      os.system('cls')
   else:
      os.system('clear')

def get_mailbox(From,To):
    if from_server['box_names'] == []:
        for x in From.list()[1]:
            name = x.decode().split('"."')[1].strip()
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
        try:
            box_select = From.select(box, readonly = False)  #open box which will have its contents copied
        except:
            print(f'MailBox \'{box}\' not exists!')
            continue
        #box_select = From.select()  #open box which will have its contents copied
        print(f'Fetching messages from \'{box}\'...')
        resp, items = From.search(None, 'ALL')
        msg_nums = items[0].split()
        print(f'{len(msg_nums)} messages to archive\n')

        length_data = len(msg_nums)

        char_='='

        try:
            to_server['box_names'][idx]
        except:
            To.create(box)
            to_server['box_names'].append(box)

        if point_msg is not None:
            msg_nums = msg_nums[point_msg-1:]
            length_data = len(msg_nums)

        for idy,msg_num in enumerate(msg_nums):
            try:
                idy_ = idy +1
                buffer = int((idy_/length_data)*100)*char_
                print(f'{length_data-idy_} messages to archive. (\'{box}\')')
                print('['+buffer.ljust(100)+']',f' {int((idy_/length_data)*100)}%')
                resp, data = From.fetch(msg_num, "(FLAGS INTERNALDATE BODY.PEEK[])") # get email
                message = data[0][1] 
                flags = imaplib.ParseFlags(data[0][0]) # get flags
                flag_str = " ".join([x.decode('utf-8') for x in flags])
                try:
                    date = imaplib.Time2Internaldate(imaplib.Internaldate2tuple(data[0][0])) #get date
                except:
                    continue
                copy_result = To.append(to_server['box_names'][idx], flag_str.upper().replace('RECENT', ''), date, message) # copy to archive

                if copy_result[0] == 'OK':
                    #del_msg = From.store(msg_num, '+FLAGS', '\\Seen') # mark for deletion
                    del_msg = From.store(msg_num, '+FLAGS', '\\Seen')

                clear()
            except:
                clear()
                continue

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
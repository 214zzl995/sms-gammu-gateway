import sys

import gammu


def load_user_data(filename='./config/credentials.txt'):
    users = {}
    with open(filename) as credentials:
        for line in credentials:
            username, password = line.partition(":")[::2]
            users[username.strip()] = password.strip()
    return users


def init_state_machine(pin, filename='./config/gammu.config'):
    # 读取gammu.config 打印配置
    with open(filename, 'r') as file:
        content = file.read()  # 读取文件内容
        print(content)  # 打印文件内容

    sm = gammu.StateMachine()
    sm.ReadConfig(Filename=filename)
    sm.Init()

    if sm.GetSecurityStatus() == 'PIN':
        if pin is None or pin == '':
            print("PIN is required.")
            sys.exit(1)
        else:
            sm.EnterSecurityCode('PIN', pin)
    return sm


def retrieve_all_sms(machine):
    status = machine.GetSMSStatus()
    all_multi_part_sms_count = status['SIMUsed'] + status['PhoneUsed'] + status['TemplatesUsed']

    all_multi_part_sms = []
    start = True

    while len(all_multi_part_sms) < all_multi_part_sms_count:
        if start:
            current_multi_part_sms = machine.GetNextSMS(Start=True, Folder=0)
            start = False
        else:
            current_multi_part_sms = machine.GetNextSMS(Location=current_multi_part_sms[0]['Location'], Folder=0)
        all_multi_part_sms.append(current_multi_part_sms)

    all_sms = gammu.LinkSMS(all_multi_part_sms)

    results = []
    for sms in all_sms:
        sms_part = sms[0]

        result = {
            "Date": str(sms_part['DateTime']),
            "Number": sms_part['Number'],
            "State": sms_part['State'],
            "Locations": [smsPart['Location'] for smsPart in sms],
        }

        decoded_sms = gammu.DecodeSMS(sms)
        if decoded_sms is None:
            result["Text"] = sms_part['Text']
        else:
            text = ""
            for entry in decoded_sms['Entries']:
                if entry['Buffer'] is not None:
                    text += entry['Buffer']

            result["Text"] = text

        results.append(result)

    return results


def delete_sms(machine, sms):
    list(map(lambda location: machine.DeleteSMS(Folder=0, Location=location), sms["Locations"]))


def encode_sms(smsInfo):
    return gammu.EncodeSMS(smsInfo)

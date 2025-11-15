#BANK MANAGEMENT PROJECT 
import json
import random
import string
from pathlib import Path


class Bank:
    database = 'data.json'
    data = [] 
    try:
        if Path(database).exists():
            with open(database, 'r', encoding='utf-8') as fs:
                content = fs.read().strip()
                if content:
                    data = json.loads(content)
                else:
                    data = []
        else:
            print("no such file exist")
    except Exception as err:
        print(f"an exception occured as {err}")
        
    @classmethod
    def __update(cls):
        with open(cls.database, 'w', encoding='utf-8') as fs:
            fs.write(json.dumps(cls.data))
    @classmethod
    def __accountgenerate(cls):
        alpha = ''.join(random.choices(string.ascii_letters, k=3))
        num = ''.join(random.choices(string.digits, k=3))
        spchar = random.choice("!@#$%^&*")
        id_parts = list(alpha + num + spchar)
        random.shuffle(id_parts)
        return "".join(id_parts)
        
    
    def createaccount(self):
       info =  {
           "name": input("Tell your name:-"),
            "age": int(input("Tell your age:-")),
            "email": input("tell your email:-"),
            "pin": int(input("Tell your 4 number pin:-")),
            "accountNo": Bank.__accountgenerate(),
            "balance": 0
        }
       if info['age'] < 18 or len(str(info['pin']))!=4:
           print("sorry you cannot create your account")
       else:
           print("account has been created succesfully")
           for i in info:
               print(f"{i}:{info[i]}")
           print("please note down your account details")
           Bank.data.append(info)
           Bank.__update()
    
    def depositmoney(self):
        accnumber = input("Please tell your account number:-").strip()
        try:
            pin = int(input("please tell your pin as well:-"))
        except ValueError:
            print("Invalid pin format")
            return
        
        # FIX: only check entries that contain both keys
        userdata_list = [i for i in Bank.data if 'accountNo' in i and 'pin' in i and i['accountNo'] == accnumber and i['pin'] == pin]
        
        if not userdata_list:
            print("Sorry no data found")
        else:
            user = userdata_list[0]
            try:
                amount = int(input("How much you want to deposit:-"))
            except ValueError:
                print("Invalid amount")
                return
            if amount > 10000 or amount <= 0:
                print("sorry the amount is too much or invalid; deposit must be between 1 and 10000")  
            else:
                user['balance'] += amount
                Bank.__update()
                print("Amount deposited successfully")
    
    
    def withdrawmoney(self):
        accnumber = input("Please tell your account number:-").strip()
        try:
            pin = int(input("please tell your pin as well:-"))
        except ValueError:
            print("Invalid pin format")
            return
        
        # FIX: only check entries that contain both keys
        userdata_list = [i for i in Bank.data if 'accountNo' in i and 'pin' in i and i['accountNo'] == accnumber and i['pin'] == pin]
        
        if not userdata_list:
            print("Sorry no data found")
        else:
            user = userdata_list[0]
            try:
                amount = int(input("How much you want to withdraw:-"))
            except ValueError:
                print("Invalid amount")
                return
            if userdata_list[0]['balance'] < amount:
                print("sorry you don't have that much money")  
            else:
                user['balance'] -= amount
                Bank.__update()
                print("Amount withdrew successfully")

    
    def showdetails(self):
        accnumber = input("Please tell your account number:-").strip()
        pin = int(input("please tell your pin as well:-"))
        userdata_list = [i for i in Bank.data if 'accountNo' in i and 'pin' in i and i['accountNo'] == accnumber and i['pin'] == pin]
        print("Your Information are: \n\n")
        for i in userdata_list[0]:
            print(f"{i}:{userdata_list[0][i]}")
            
    
    def updatedetails(self):
        accnumber = input("Please tell your account number:-").strip()
        pin = int(input("please tell your pin as well:-"))
        userdata_list = [i for i in Bank.data if 'accountNo' in i and 'pin' in i and i['accountNo'] == accnumber and i['pin'] == pin]
        
        if userdata_list == False:
            print("no such user found")
        else:
            print("You cannot change the age, account number, balance") 
            
            print("Fill the details for change or leave it empty if no change")   
            newdata = {
                "name": input("please tell new name or press enter:"),
                "email": input("Please tell your new Email or press enter to skip:"),
                "pin":input("Enter new pin or press enter to skip:")
            }
            
            if newdata["name"] == "":
                newdata["name"] = userdata_list[0]['name']
            
            if newdata["email"] == "":
                newdata["email"] = userdata_list[0]['email']
            
            if newdata["pin"] == "":
                newdata["pin"] = userdata_list[0]['pin']
                
            newdata['age'] = userdata_list[0]['age']
            newdata['accountNo'] = userdata_list[0]['accountNo']
            newdata['balance'] = userdata_list[0]['balance']
            
            if type(newdata["pin"]) == str:
                newdata["pin"] = int(newdata["pin"])
            
            for i in newdata:
                if newdata[i] == userdata_list[0][i]:
                    continue
                else:
                    userdata_list[0][i] = newdata[i]  
            Bank.__update()
            print("details updtated succesfully")
            
    def Delete(self):
        accnumber = input("Please tell your account number:-").strip()
        pin = int(input("please tell your pin as well:-"))
        userdata_list = [i for i in Bank.data if 'accountNo' in i and 'pin' in i and i['accountNo'] == accnumber and i['pin'] == pin]
        
        if userdata_list == False:
            print("sorry no such data exist") 
        else:
            check = input("press y if you actually want to delete the account or press n")  
            if check == 'n' or check == 'N':
                print("bypassed")
            else:
                index = Bank.data.index(userdata_list[0])
                Bank.data.pop(index)
                print("account deleted successfully")
                Bank.__update

                    
            
user = Bank()
# USER INPUT
print("press 1 for creating an account")
print("press 2 for deposit the money in the bank")
print("press 3 for withdrawing the money")
print("press 4 for details:")
print("press 5 for updating the details")
print("press 6 for deleting your account")

#INPUT
check = int(input("tell your response:-"))

if check == 1:
    user.createaccount()
    
if check == 2:
    user.depositmoney()

if check == 3:
    user.withdrawmoney()
    
if check == 4:
    user.showdetails()
 
if check == 5:
    user.updatedetails() 
   
if check == 6:
    user.Delete()
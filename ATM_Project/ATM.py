class ATM:
  # constructor (Special Function)
  def __init__(self) :
    self.pin = ''
    self.balance = 0
    self.menu()


  def menu(self):
    user_input = input("""
    Hi how can I help you?
    1. Press 1 to create pin
    2. Press 2 to change pin
    3. Press 3 to check balance
    4. Press 4 to withdraw
    5. Anything else to exit
    
     """)
    
    if user_input == '1':
      # create pin  
      self.create_pin() 

    elif user_input == '2':
      # change pin
      self.change_pin()
     
    elif user_input == '3':
      # check balance
      self.check_balance()
    elif user_input == '4':
      # withdraw
      self.withdraw()
    else:
      # exit
      exit()

  def create_pin(self):
    user_pin = input("Enter your pin: ")
    self.pin = user_pin

    user_balance = int(input("Enter balance:"))
    self.balance = user_balance
    print("Pin created successfully:") 
    self.menu()

  def  change_pin(self):
    old_pin = input("Enter your old pin:")

    if old_pin == self.pin:
      # let him change pin
      new_pin = input("Enter your pin:")
      self.pin = new_pin
      print("Change pin successfully")

    else:
      print("Not possible")
    self.menu()
  
  def check_balance(self):
   user_pin = input("Enter your pin")

   if user_pin == self.pin :
    print(f"your balance is  {self.balance} only")
     
   else :
    print("Try again!! Enter correct password please...")
   self.menu()

  def  withdraw(self):
    user_pin = input("Enter your pin")

    if user_pin == self.pin :
      print(f"your balance is  {self.balance} only")
      amount = int(input("Enter withdraw amount: "))
      if amount <= self.balance:
        self.balance = self.balance - amount
        print(f"Successfully Withdraw {amount}")
        print(f"your balance is  {self.balance} only")
      else:
        print("Garib hai tu!! Limit cross kyun kiya??")
     
    else :
      print("Try again!! Enter correct password please...")
   
    self.menu()

obj = ATM()
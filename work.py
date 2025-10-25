import email
class Students:
    discount_amt = 200
    def __init__(self,first_name , last_name, tuition_fee):
        self.first_name = first_name
        self.last_name = last_name
        self.email_adress = first_name + '.' + last_name + '@std.kyrenia.edu.tr'
        self.tuition_fee = tuition_fee
        
    def full_name(self):
        return '{}{}'.format(self.first_name,self.last_name)
    
    def apply_discount(self):
        self.tuition_fee = int(self.tuition_fee - self.discount_amt)
        
    def __repr__(self):
        return "Students({},{},{})".format(self.first_name,self.last_name,self.tuition_fee)
    
    def __str__(self):
        return '{} - {}'.format(self.full_name,self.email_adress)
    
    def __add__(self,other):
        return self.tuition_fee + other.tuition_fee
        
    
K2020xxx = Students('Kerem','A',16000)
K2021xxx = Students('Ceylan','C',16000)
print(K2020xxx + K2021xxx)

class Human:
    def __init__(self,name,age,nationality,adress):
        self.name = name
        self.age = age
        self.nationality = nationality
        self.adress = adress
        
    
    def work(self):
        print("This person is hardworking ")
        
    def walking(self):
        print("This person is going to the lab ")
    
class Student(Human):
    def study(self):
        print("This person is studying")
    def homework(self):
        print("This person is doing homework")

class Teacher(Human):
    def teaching(self):
        print("this person is teaching a lesson")
    def reading(self):
        print("This person is reading exam papers")

student_1 = Student("Kerem",22,"Turkey","Alsancak")
teacher_1 = Teacher("Mehmet",32,"Turkey","Girne")

print(student_1.name , student_1.age , student_1.nationality , student_1.adress)
print(teacher_1.name , teacher_1.age , teacher_1.nationality , teacher_1.adress)
student_1.study()
teacher_1.teaching()
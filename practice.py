class Engine:
    def __init__(self,horsepower):
        self.horsepower = horsepower
        
class Wheel:
    def __init__(self,size):
        self.size = size
        
class Car:
    def __init__(self,make,brand,horsepower,wheel_size):
        self.make = make
        self.brand = brand
        self.engine = Engine(horsepower)
        self.wheel = [Wheel(wheel_size) for _ in range (4) ]
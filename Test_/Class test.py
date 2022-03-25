import time

class Schüler:
    def __init__(self, first, last, age,):
        self.first = first
        self.last = last
        self.age = age
    def fullname(self):
        return '{} {}'.format(self.first, self.last)
    def allstats(self):
        return '{} {} ist {} Jahre alt.'.format(self.first, self.last, self.age)

schü_1 = Schüler('Egor', 'Zakhartsev', 18)
schü_2 = Schüler('Semion', 'Kirschbaum', 19)

print(schü_1.allstats())
print(schü_2.allstats())

#include <stdio.h>
#include <stdlib.h>

typedef struct Animal {
    void(*speak)(struct Animal*);
} Animal;

void Animal_speak(Animal* self) {
    printf("Animal speaks\n");

}
Animal* Animal_new() {
    Animal *animal = (Animal*)malloc(sizeof(Animal));
    animal->speak = Animal_speak;
    
    return animal;
}

typedef struct Dog {
    Animal base;
} Dog;

void Dog_speak(Animal* self) {
    printf("Dog barks\n");
}

Dog* Dog_new() {
    Dog *dog = (Dog*)malloc(sizeof(Dog));
    dog->base.speak = Dog_speak;
    
    return dog;
}

int main() {
    Animal* animal = Animal_new();
    animal->speak(animal);
    
    Dog* dog = Dog_new();
    dog->base.speak((Animal*)dog);
    
    return 0;
}


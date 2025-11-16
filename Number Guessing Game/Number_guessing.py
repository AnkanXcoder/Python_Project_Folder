import random

r = random.randint(1, 100)

while True:
    guess = int(input("Guess the number between 1 and 100: "))

    if guess == r:
        print(f"You guessed it right! The number was {r}. 🎯")
        break
    elif guess > r:
        print("Too high! Try a smaller number.")
    else:
        print("Too low! Try a bigger number.")

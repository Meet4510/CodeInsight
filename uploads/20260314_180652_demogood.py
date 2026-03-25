def is_prime(number: int) -> bool:
    """
    Check if a number is prime.

    Args:
        number (int): Number to check

    Returns:
        bool: True if prime, False otherwise
    """

    if number <= 1:
        return False

    for i in range(2, int(number ** 0.5) + 1):
        if number % i == 0:
            return False

    return True


def main():
    try:
        num = int(input("Enter a number: "))

        if is_prime(num):
            print(f"{num} is a prime number.")
        else:
            print(f"{num} is not a prime number.")

    except ValueError:
        print("Please enter a valid integer.")


if __name__ == "__main__":
    main()
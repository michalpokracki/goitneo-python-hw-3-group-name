from collections import UserDict, defaultdict
import re
from datetime import datetime


class PhoneError(Exception):
    pass


class DateError(Exception):
    pass


class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)


class Name(Field):
    pass


class Phone(Field):
    def __init__(self, value):
        super().__init__(value)
        if len(value) == 10 and value.isdigit():
            self.value = value
        else:
            raise PhoneError()


class Birthday(Field):
    def __init__(self, value=None):
        super().__init__(value)
        if re.search("^(0[1-9]|[12][0-9]|3[01])[.](0[1-9]|1[012])[.](19|20)[0-9]{2}$", value):
            self.value = value
        else:
            raise DateError()


class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.birthday = None
        self.phones = []

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def edit_phone(self, old_phone, new_phone):
        for phone in self.phones:
            idx = None
            if phone.value == old_phone:
                idx = self.phones.index(phone)
            self.phones[idx] = Phone(new_phone)

    def find_phone(self, searching_phone):
        for phone in self.phones:
            if phone.value == searching_phone:
                return True
        return False

    def remove_phone(self, deleting_phone):
        for phone in self.phones:
            if phone.value == deleting_phone:
                self.phones.remove(phone)

    def add_birthday(self, birthday):
        self.birthday = Birthday(birthday)

    def __str__(self):
        return f"Contact name: {self.name.value}, phones: {'; '.join(phone.value for phone in self.phones)}"


class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        del self.data[name]

    def get_birthdays_per_week(self):
        result_dict = defaultdict(list)
        result_array = []
        today = datetime.today().date()

        for user in self.data.values():
            name = user.name.value
            birthday = datetime.strptime(user.birthday.value, "%d.%m.%Y").date()
            birthday_this_year = birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year.replace(year=today.year + 1)
                continue

            delta_days = (birthday_this_year - today).days

            if delta_days < 7:
                weekday = birthday_this_year.strftime("%A")
                work_weekday = "Monday" if weekday in ["Saturday", "Sunday"] else weekday
                result_dict[work_weekday].append(name)

        for day, names in result_dict.items():
            result_array.append(f"{day}: {', '.join(names)}")

        return '\n'.join(result_array)


def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, *args


def input_error(func):
    def inner(args, kwargs):
        try:
            return func(args, kwargs)
        except DateError:
            return "Date not in the format DD.MM.YYYY"
        except PhoneError:
            return "The phone number needs to have 10 digits."
        except ValueError:
            return "Give me name and phone please."
        except KeyError:
            return "The name is not in contacts."
        except IndexError:
            return "Enter user name."

    return inner


@input_error
def add_contact(args, book):
    record = Record(args[0])
    record.add_phone(args[1])
    book.add_record(record)
    return "Contact added."


@input_error
def change_contact(args, book):
    record = book.find(args[0])
    if record:
        record.edit_phone(record.phones[0].value, args[1])
    return "Contact updated."


@input_error
def show_phone(args, book):
    result = []
    record = book.find(args[0])
    if record:
        for phone in record.phones:
            result.append(phone.value)
    return ', '.join(result)


def show_all(book):
    result = []
    for record in book.data.values():
        result.append(str(record))
    return "\n".join(result)


@input_error
def add_birthday(args, book):
    record = book.find(args[0])
    record.add_birthday(args[1])
    return "Birthday added."


@input_error
def show_birthday(args, book):
    record = book.find(args[0])
    if record:
        return record.birthday.value


def main():
    book = AddressBook()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, *args = parse_input(user_input)

        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_contact(args, book))
        elif command == "phone":
            print(show_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "birthdays":
            print(book.get_birthdays_per_week())
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        else:
            print("Invalid command.")


if __name__ == "__main__":
    main()

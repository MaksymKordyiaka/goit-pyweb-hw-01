from collections import UserDict
from datetime import datetime
import pickle

class Field:
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return str(self.value)

class Name(Field):
    def __init__(self, value):
        if not value:
            raise ValueError("Name cannot be empty")
        super().__init__(value)

class Phone(Field):
    def __init__(self, value):
        try:
            if not value.isdigit() or len(value) != 10:
                raise ValueError("Phone number must contain 10 digits")
            super().__init__(value)
        except AttributeError:
            raise AttributeError('Invalid format number. Use 10 digits')

class Birthday(Field):
    def __init__(self, value):
        super().__init__(value)
        try:
            datetime.strptime(value, "%d.%m.%Y")
        except ValueError:
            raise ValueError("Invalid date format. Use DD.MM.YYYY")
        except TypeError:
            raise TypeError("Invalid date format. Use DD.MM.YYYY")

class Record:
    def __init__(self, name):
        self.name = Name(name)
        self.phones = []
        self.birthday = None

    def add_birthday(self, b_day):
        self.birthday = Birthday(b_day)

    def add_phone(self, phone):
        self.phones.append(Phone(phone))

    def remove_phone(self, phone):
        self.phones = [p for p in self.phones if p.value != phone]

    def edit_phone(self, old_phone, new_phone):
        old_phone_obj = self.find_phone(old_phone)
        if old_phone_obj:
            if not new_phone.isdigit() or len(new_phone) != 10:
                raise ValueError("New phone number must contain 10 digits")
            old_phone_obj.value = new_phone
        else:
            raise ValueError("Phone number not found.")

    def find_phone(self, phone):
        for p in self.phones:
            if p.value == phone:
                return p
        return None

    def __str__(self):
        return f"Contact name: {str(self.name)}, phone: {'; '.join(str(p) for p in self.phones)}, birthdate: {self.birthday}"

class AddressBook(UserDict):
    def add_record(self, record):
        self.data[record.name.value] = record

    def find(self, name):
        return self.data.get(name)

    def delete(self, name):
        if name in self.data:
            del self.data[name]
        else:
            raise ValueError(f"Record with name '{name}' not found in the address book.")

    def get_upcoming_birthdays(self):
        today = datetime.today().date()
        birthdays = []
        for user in self.data.values():
            if user.birthday:
                birth_date = datetime.strptime(user.birthday.value, '%d.%m.%Y').date().replace(year=today.year)
                difference_date = (birth_date - today).days
                if 0 <= difference_date <= 7:
                    if birth_date.isoweekday() < 6:
                        birthdays.append({'name': user.name.value, 'birthday': birth_date.strftime('%d.%m.%Y')})
                    else:
                        birthdays.append({'name': user.name.value, 'birthday': birth_date.strftime('%d.%m.%Y')})
        return birthdays

def parse_input(user_input):
    cmd, *args = user_input.split()
    cmd = cmd.strip().lower()
    return cmd, args

def input_error(func):
    def inner(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except (KeyError, ValueError, IndexError, AttributeError) as error:
            if isinstance(error, ValueError):
                return 'Error! if you want to:\n' \
                       'add contact: you must input ("add" username phone).\n' \
                       'change phone: you must input ("change" username old_phone new_phone) or no contacts.\n' \
                       'get phone: you must input ("phone" username)\n'\
                       'add-birthday: you must input("add-birthday" username DD.MM.YYYY)\n'\
                       'show-birthday: you must input("show-birthday" username)\n'
            elif isinstance(error, AttributeError):
                return 'Atribute error'
            elif isinstance(error, KeyError):
                return 'Key error'
            elif isinstance(error, IndexError):
                return 'Index error'
    return inner

@input_error
def add_contact(args, book: AddressBook):
    name, phone = args
    record = book.find(name)
    message = "Contact updated."
    if record is None:
        record = Record(name)
        book.add_record(record)
        message = "Contact added."
    if phone:
        record.add_phone(phone)
    return message

@input_error
def change_phone(args, book: AddressBook):
    name, old_phone, new_phone = args
    record = book.find(name)
    if record:
        record.edit_phone(old_phone, new_phone)
        return f"Phone number for '{name}' changed."
    else:
        return f"Contact {name} not found."

def show_all(book: AddressBook):
    if not book:
        return 'No contacts available, you need to (add "username" "phone")'
    else:
        result = ''
        for name, phone in book.items():
            result += f"{name}: {phone}\n"
        return result.strip()

@input_error
def get_phone(args, book: AddressBook):
    name, = args
    record = book.find(name)
    if record:
        return f"Phone number for '{name}': {', '.join(str(phone) for phone in record.phones)}"
    else:
        return f"Contact {name} not found."

@input_error
def add_birthday(args, book: AddressBook):
    name, birthday = args
    record = book.find(name)
    if record:
        record.add_birthday(birthday)
        return f"Birthday added for '{name}'."
    else:
        return f"Contact '{name}' not found."

@input_error
def show_birthday(args, book: AddressBook):
    name, = args
    record = book.find(name)
    if record:
        if record.birthday:
            return f"Birthday for '{name}': {record.birthday}"
        else:
            return f"No birthday found for '{name}'. Please add a birthday using 'add-birthday' command."
    else:
        return f"No contact found for '{name}'."

def birthdays(book: AddressBook):
    upcoming_birthdays = book.get_upcoming_birthdays()
    if not upcoming_birthdays:
        return "No upcoming birthdays"
    else:
        return "\n".join(f"Upcoming birthday next week for '{b['name']}': {b['birthday']}" for b in upcoming_birthdays)

def save_data(book, filename="addressbook.pkl"):
    with open(filename, "wb") as f:
        pickle.dump(book, f)

def load_data(filename="addressbook.pkl"):
    try:
        with open(filename, "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return AddressBook()

def main():
    book = load_data()
    print("Welcome to the assistant bot!")
    while True:
        user_input = input("Enter a command: ")
        command, args = parse_input(user_input)
        if command in ["close", "exit"]:
            print("Good bye!")
            break
        elif command == "hello":
            print("How can I help you?")
        elif command == "add":
            print(add_contact(args, book))
        elif command == "change":
            print(change_phone(args, book))
        elif command == "phone":
            print(get_phone(args, book))
        elif command == "all":
            print(show_all(book))
        elif command == "add-birthday":
            print(add_birthday(args, book))
        elif command == "show-birthday":
            print(show_birthday(args, book))
        elif command == "birthdays":
            print(birthdays(book))
        else:
            print("Invalid command.")
    save_data(book)

if __name__ == '__main__':
    main()
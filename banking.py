import random
import math
from sqlite3 import connect


class BankAccount:
    Data = 'card.s3db'

    def __init__(self):
        self.balance = 0
        self.card_number = 0
        self.pin = 0
        self.card_to_check = 0
        self.pin_to_check = 0
        self.card_luhn = 0
        self.checksum = None
        self.conn = connect(BankAccount.Data)
        self.conn.execute("""CREATE TABLE IF NOT EXISTS card (
                            id          INTEGER PRIMARY KEY AUTOINCREMENT,
                            number      TEXT,
                            pin         TEXT,
                            balance     INTEGER DEFAULT 0 );
                            """)
        self.conn.commit()

    def create_card(self):
        self.card_luhn = random.randint((4 * (10 ** 15)), (4 * (10 ** 15) + 999999999))
        test = self.check_luhn()
        if test is True:
            self.card_number = self.card_luhn
        else:
            c = list(str(self.card_luhn))
            c.pop()
            self.card_number = int("".join(map(str, c)) + str(self.checksum))
        number = self.conn.execute('SELECT number FROM card WHERE number = ?', (self.card_number, )).fetchone()
        if number is not None:
            self.create_card()
        else:
            self.pin = f'{random.randint(0, 9999):04}'
            self.conn.execute('INSERT INTO card (number, pin, balance) VALUES (?, ?, ?)', (self.card_number, self.pin, self.balance))
            self.conn.commit()
            print(f"Your card number:\n{self.card_number}")
            print(f"Your card PIN:\n{self.pin}\n")

    def check_luhn(self):
        c = list(str(self.card_luhn))
        for i in range(0, (len(c) - 1), 2):
            c[i] = int(c[i]) * 2
        num = 0
        for i in range(0, (len(c) - 1)):
            c[i] = int(c[i])
            if c[i] > 9:
                c[i] -= 9
            num += c[i]
        self.checksum = math.ceil(num / 10.0) * 10 - num
        if c[-1] == str(self.checksum):
            return True
        else:
            return False

    def delete_card(self):
        self.conn.execute(f'DELETE FROM card WHERE number = {self.card_to_check};')
        self.conn.commit()
        print("\nThe account has been closed!\n")
        # The next to readjust IDs
        self.conn.execute('PRAGMA foreign_keys=off;')
        self.conn.execute('BEGIN TRANSACTION;')
        self.conn.execute("""CREATE TABLE IF NOT EXISTS mycard (
                        id          INTEGER PRIMARY KEY AUTOINCREMENT,
                        number      TEXT,
                        pin         TEXT,
                        balance     INTEGER DEFAULT 0 );
                        """)
        self.conn.execute("""INSERT INTO mycard (number, pin, balance)
                        SELECT number, pin, balance
                        FROM card;
                        """)
        self.conn.execute('DROP TABLE card;')
        self.conn.execute('ALTER TABLE mycard RENAME TO card;')
        self.conn.commit()

    def transfer_money(self):
        print("\nTransfer")
        self.card_luhn = int(input("Enter card number:\n"))
        test = self.check_luhn()
        card_val = self.conn.execute('SELECT number FROM card WHERE number = ?', (self.card_luhn, )).fetchone()
        if test is False:
            print("Probably you made mistake in the card number. Please try again!\n")
        elif card_val is not None:
            if self.card_to_check == self.card_luhn:
                print("You can't transfer money to the same account!\n")
            else:
                money = int(input("Enter how much money you want to transfer:\n"))
                if money > self.balance:
                    print("Not enough money!\n")
                else:
                    print("Success!\n")
                    self.conn.execute(f'UPDATE card SET balance = {self.balance - money} WHERE number = {self.card_to_check};')
                    self.balance = self.conn.execute('SELECT balance FROM card WHERE number = ?', (self.card_to_check, )).fetchone()[0]
                    transfer_acc_initial_balance = self.conn.execute('SELECT balance FROM card WHERE number = ?', (self.card_luhn, )).fetchone()[0]
                    self.conn.execute(f'UPDATE card SET balance = {transfer_acc_initial_balance + money} WHERE number = {self.card_luhn};')
                    self.conn.commit()
        else:
            print("Such a card does not exist.")

    def logging(self):
        self.card_to_check = int(input("\nEnter your card number:\n"))
        self.pin_to_check = input("Enter your PIN:\n")
        card_val = self.conn.execute('SELECT number FROM card WHERE number = ?', (self.card_to_check, )).fetchone()
        if card_val is not None:
            pin_val = self.conn.execute('SELECT pin FROM card WHERE number = ?', (self.card_to_check, )).fetchone()[0]
            if pin_val == self.pin_to_check:
                print("\nYou have successfully logged in!\n")
                self.balance = self.conn.execute('SELECT balance FROM card WHERE number = ?', (self.card_to_check, )).fetchone()[0]
                self.conn.commit()
                while True:
                    choice = int(input("1. Balance\n"
                                       "2. Add income\n"
                                       "3. Do transfer\n"
                                       "4. Close account\n"
                                       "5. Log out\n"
                                       "0. Exit\n"))
                    if choice == 1:
                        print(f"\nBalance: {self.balance}\n")
                    elif choice == 2:
                        adding = int(input("\nEnter income:\n"))
                        self.conn.execute(f'UPDATE card SET balance = {self.balance + adding} WHERE number = {self.card_to_check};')
                        self.balance = self.conn.execute('SELECT balance FROM card WHERE number = ?', (self.card_to_check, )).fetchone()[0]
                        self.conn.commit()
                    elif choice == 3:
                        self.transfer_money()
                    elif choice == 4:
                        self.delete_card()
                        break
                    elif choice == 5:
                        print()
                        break
                    elif choice == 0:
                        print("\nBye!")
                        exit()
            else:
                print("Wrong card number or PIN!\n")

        else:
            print("Wrong card number or PIN!\n")

    @staticmethod
    def start():
        while True:
            choose = int(input("1. Create an account\n"
                               "2. Log into account\n"
                               "0. Exit\n"))
            if choose == 1:
                print("\nYour card has been created")
                account.create_card()

            elif choose == 2:
                account.logging()

            elif choose == 0:
                print("\nBye!")
                exit()


account = BankAccount()
account.start()

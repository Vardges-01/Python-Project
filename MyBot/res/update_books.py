import sqlite3
import os

db = sqlite3.connect('/home/vardges/Desktop/GitHub/Python-Project/MyBot/DB/subjectname.db')
cursor = db.cursor()

query = """ DELETE FROM books_names  """
cursor.execute(query)
db.commit()

def insert_books(books_list,book_type,book_leng):

	for x in books_list:

		book_name = x.rstrip(".pdf")
		addr = f"res/Books/{book_type}/{book_leng}/{x}" 
		if book_leng == "En":
			query = f""" INSERT INTO books_names (type, name, en_addres) VALUES('{book_type}','{book_name}', '{addr}')"""
			cursor.execute(query)
		else:
			query = f""" UPDATE books_names SET ru_addres = '{addr}' WHERE name = '{book_name}'"""
			cursor.execute(query)

	db.commit()

subj_names = os.listdir("Books")
for book_type in subj_names:
	print(book_type)
	books_list=os.listdir(f"Books/{book_type}/En")
	insert_books(books_list,book_type,"En")

	books_list=os.listdir(f"Books/{book_type}/Ru")
	insert_books(books_list,book_type,"Ru")

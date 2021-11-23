import telebot
import config
import sqlite3
import os

from telebot import types

bot = telebot.TeleBot(config.TOKEN)

admin_key = False

@bot.message_handler(commands=['start'])
def welcome(message):

	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()
	us_id = message.from_user.id
	us_name = "{0.first_name} {0.last_name}".format(message.from_user, bot.get_me())
	query = f""" INSERT OR IGNORE INTO user_info (user_id, user_name) VALUES ({us_id}, '{us_name}')"""
	cursor.execute(query)
	records=cursor.fetchall()
	db.commit()

	global admin_key
	admin_id = [550868377]

	stic = open('res/hello.webp', 'rb')
	bot.send_sticker(message.chat.id, stic)

	# keyboard
	markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
	item1 = types.KeyboardButton("📚 Գրքեր")
	item2 = types.KeyboardButton("Որոնել 🔎")
	item3 = types.KeyboardButton("Առաջարկել գիրք 📖")
	item4 = types.KeyboardButton("Update 📥")

	if message.from_user.id in admin_id:
		admin_key = True
		markup.add(item1,item2,item3,item4)
	else:
		markup.add(item1,item2,item3)


	bot.send_message(message.chat.id, "Բարի գալուստ, {0.first_name}!\nԵս - <b>{1.first_name}</b>֊ն եմ.\nBot֊ը ստեղծված է նրա համար որ օգնի հեշտ գտնել գրքեր <b>Code Republic</b>֊ի գրադարանից.".format(message.from_user, bot.get_me()), parse_mode='html',reply_markup = markup)


rec_key = False
search_key = False

@bot.message_handler(content_types=["text"])
def text(message):
	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()

	global rec_key
	global search_key

	if message.chat.type == 'private':
		if message.text == '📚 Գրքեր':
			item1 = []
			query = """ SELECT DISTINCT type FROM books_names"""
			cursor.execute(query)
			records=cursor.fetchall()
			db.commit()

			markup=types.InlineKeyboardMarkup(row_width=2)

			for x in records:
				item1.append(types.InlineKeyboardButton(x[0], callback_data=x[0]))

			markup.add(*item1)

			bot.send_message(message.chat.id, "Որ Լեզուն?", reply_markup=markup)

		elif message.text == "Առաջարկել գիրք 📖":
			rec_key=True
			bot.send_message(message.chat.id, "Գրեք գրքի անվանումը․․")

		elif message.text == "Որոնել 🔎":
			search_key = True
			bot.send_message(message.chat.id, "Գրեք գրքի անվանումը կամ հեղինակին․")

		elif message.text == "Update 📥" and admin_key == True:
			update_db(message.chat.id)

		elif rec_key:

			query = f""" INSERT INTO Recommended_books(name) VALUES('{message.text}') """
			cursor.execute(query)
			db.commit()
			bot.send_message(message.chat.id, "Շնորհակալություն խորհրդի համար)")
			rec_key=False

		elif search_key:
			search_key = False
			show_search_books(message.text, message.chat.id)


read_key = False
book_id = 0

@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):

	global read_key
	global book_id
	lngs = []

	try:
		if call.message:
	
			subj_names = os.listdir("res/Books")
			for book_type in subj_names:
				lngs.append(book_type)

			if call.data in lngs:
				show_books(call.data, call.message)
				read_key = True

			elif read_key == True:
				book_id = call.data
				read_key = False

				keyb_books = types.InlineKeyboardMarkup(row_width=2)
				leng1 = types.InlineKeyboardButton(text="En 🇺🇸", callback_data="En")
				leng2 = types.InlineKeyboardButton(text="Rus 🇷🇺", callback_data="Ru")
				keyb_books.add(leng1,leng2)


				bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text = "Ընտրեք լեզուն ?", reply_markup = keyb_books)

			elif call.data == "En" or call.data == "Ru":
				read_book(book_id, call.data, call.message)


	except Exception as e:
		print(repr(e))


# Update DB information
def update_db(botchat_id):
	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()

	query = """ DELETE FROM books_names  """
	cursor.execute(query)
	db.commit()
	subj_names = os.listdir("res/Books")
	for book_type in subj_names:
		books_list=os.listdir(f"res/Books/{book_type}/En")
		insert_books(books_list,book_type,"En")

		books_list=os.listdir(f"res/Books/{book_type}/Ru")
		insert_books(books_list,book_type,"Ru")

	bot.send_message(botchat_id, "Տվյալները թարմացված են 📋🎉")

def insert_books(books_list,book_type,book_leng):

	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()

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


def show_search_books(file_name,botchat):

	global read_key
	read_key = True

	item1=[]
	db=sqlite3.connect('DB/subjectname.db')
	cursor=db.cursor()

	query=f""" SELECT id,name FROM books_names WHERE name LIKE '%{file_name}%' ORDER BY name """
	cursor.execute(query)
	records=cursor.fetchall()
	db.commit()

	book_count = len(records)

	if book_count == 0:
		bot.send_message(botchat, f"Գտնվել է {book_count} գիրք 😔 ")
		return

	markup=types.InlineKeyboardMarkup(row_width=4)
	book_list=""

	for y, x in enumerate(records, 1):
		book_list+=f"{y} ) {x[1]}\n---------------------------------------\n"
		item1.append(types.InlineKeyboardButton(y, callback_data = x[0]))

	markup.add(*item1)

	bot.send_message(botchat, f"Գտնվել է {book_count} գիրք.\n\n{book_list}", reply_markup=markup)


# Show books for User
def show_books(book_type,botchat):

	item1=[]
	db=sqlite3.connect('DB/subjectname.db')
	cursor=db.cursor()

	query=f""" SELECT id,name FROM books_names WHERE type = '{book_type}' ORDER BY name """
	cursor.execute(query)
	records=cursor.fetchall()
	db.commit()

	markup=types.InlineKeyboardMarkup(row_width=4)
	book_list=""

	for y, x in enumerate(records, 1):
		book_list+=f"{y} ) {x[1]}\n---------------------------------------\n"
		item1.append(types.InlineKeyboardButton(y, callback_data = x[0]))

	markup.add(*item1)

	bot.edit_message_text(chat_id=botchat.chat.id, message_id=botchat.message_id, text=book_list, reply_markup=markup)



# Read Book and Send
def read_book(book_id, book_leng,botchat_id):
	db=sqlite3.connect('DB/subjectname.db')
	cursor=db.cursor()

	if book_leng == "En":
		query = f""" SELECT en_addres FROM books_names WHERE id = {book_id} """
	elif book_leng == "Ru":
		query = f""" SELECT ru_addres FROM books_names WHERE id = {book_id} """


	cursor.execute(query)
	records = cursor.fetchall()
	db.commit()
	res = str(records[0][0])
	if res == "None":
		bot.send_message(botchat_id.chat.id, "Այս լեզվով չկա, միգուցե ուրիշ լեզու ընտրեք ? 🤔")
	else:
		file = open(res, "rb")
		bot.send_document(botchat_id.chat.id,file)



# RUN
bot.polling(none_stop=True)
import telebot
import config
import sqlite3

from telebot import types

bot = telebot.TeleBot(config.TOKEN)


@bot.message_handler(commands=['start'])
def welcome(message):

	stic = open('res/hello.webp', 'rb')
	bot.send_sticker(message.chat.id, stic)

	# keyboard
	markup = types.ReplyKeyboardMarkup(resize_keyboard = True, row_width = 2)
	item1 = types.KeyboardButton("📚 Գրքեր")
	item2 = types.KeyboardButton("Որոնել 🔎  (Շուտով)")
	item3 = types.KeyboardButton("Առաջարկել գիրք 📖")

	markup.add(item1,item3,item2)

	bot.send_message(message.chat.id, "Բարի գալուստ, {0.first_name}!\nԵս - <b>{1.first_name}</b>֊ն եմ.\nBot֊ը ստեղծվածա նրա համար որ օգնի հեշտ գտնել գրքեր <b>Code Republic</b>֊ի գրադարանից.".format(message.from_user, bot.get_me()), parse_mode='html',reply_markup = markup)


search_key = False

@bot.message_handler(content_types=["text"])
def text(message):
	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()

	global search_key

	if message.chat.type == 'private':
		if message.text == '📚 Գրքեր':
			search_key = False
			item1 = []
			query = """ SELECT * FROM subname """
			cursor.execute(query)
			records = cursor.fetchall()
			db.commit()

			markup = types.InlineKeyboardMarkup(row_width = 1)

			for x in records:
				item1.append(types.InlineKeyboardButton(x[1], callback_data = x[1]))

			for x in item1:
				markup.add(x)

			bot.send_message(message.chat.id, "Որ Լեզուն?", reply_markup = markup)

		if message.text == "Առաջարկել գիրք 📖":
			search_key = True
			bot.send_message(message.chat.id, "Գրեք գրքի անվանումը․․")

		elif search_key == True:

			query = f""" INSERT INTO Recommended_books(name) VALUES('{message.text}') """
			cursor.execute(query)
			db.commit()
			bot.send_message(message.chat.id, "Շնորհակալություն խորհրդի համար)")





read_key = False
table_name = ""
book_name = ""

@bot.callback_query_handler(func=lambda call:True)
def callback_inline(call):

	global read_key
	global table_name
	global book_name

	try:
		if call.message:
			if call.data == "Cpp" or call.data == "Java" or call.data == "Js" or call.data == "Python" or call.data == "DB" or call.data == "OS" or call.data == "Algorithm":
				show_books(call.data, call.message)
				table_name = call.data
				read_key = True

			elif read_key == True:
				book_name = call.data
				read_key = False

				keyb_books = types.InlineKeyboardMarkup(row_width = 2)
				leng1 = types.InlineKeyboardButton(text = "En 🇺🇸", callback_data = "En")
				leng2 = types.InlineKeyboardButton(text = "Rus 🇷🇺", callback_data = "Rus")
				keyb_books.add(leng1,leng2)


				bot.edit_message_text(chat_id = call.message.chat.id, message_id = call.message.message_id, text = "Ընտրեք լեզուն ?", reply_markup = keyb_books)

			elif call.data == "En" or call.data == "Rus":
				read_book(table_name,book_name, call.data, call.message)


	except Exception as e:
		print(repr(e))


def show_books(table_name,botchat):
	item1 = []
	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()

	query = f""" SELECT id,name,autor FROM {table_name} """
	cursor.execute(query)
	records = cursor.fetchall()
	db.commit()

	markup = types.InlineKeyboardMarkup(row_width = 4)
	book_list = ""
	for x in records:
		book_list+=f"{x[0]} ) {x[1]} - ( {x[2]} )\n---------------------------------------\n"
		item1.append(types.InlineKeyboardButton(x[0], callback_data = x[1]))

	# Show inline keyboard
	for i in item1:
		markup.add(i)

	bot.edit_message_text(chat_id = botchat.chat.id, message_id = botchat.message_id, text = book_list, reply_markup = markup)






# Read Book and Send
def read_book(table_name,book_name, book_leng,botchat_id):
	db = sqlite3.connect('DB/subjectname.db')
	cursor = db.cursor()

	if book_leng == "En":
		query = f""" SELECT en_addres FROM {table_name} WHERE name = '{book_name}' """
	elif book_leng == "Rus":
		query = f""" SELECT rus_addres FROM {table_name} WHERE name = '{book_name}' """


	cursor.execute(query)
	records = cursor.fetchall()
	db.commit()
	res = str(records[0][0])
	if res == "None":
		bot.send_message(botchat_id.chat.id, "Էս լեզվով չկա, կարողա՞ ուրիշ լեզու ընտրես 🤔")
	else:
		file = open(res, "rb")
		bot.send_document(botchat_id.chat.id,file)



# RUN
bot.polling(none_stop=True)

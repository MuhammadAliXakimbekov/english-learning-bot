import asyncio
import logging
import os
import threading
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN, RATE_LIMIT_PER_USER
from utils.rate_limiter import rate_limiter
from services.gemini_service import gemini_service
from services.voice_service import voice_service

# Set up logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Flask app for health checks (required for Render.com)
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint for deployment platforms"""
    return {'status': 'healthy', 'service': 'Education Bot', 'version': '1.0'}, 200

@app.route('/')
def home():
    """Root endpoint"""
    return {'message': 'Education Bot is running!', 'status': 'active'}, 200

def run_flask():
    """Run Flask app in a separate thread"""
    port = int(os.environ.get('PORT', 10000))
    app.run(host='0.0.0.0', port=port, debug=False, use_reloader=False)

# Store user modes
user_modes = {}

# Library books data with local file paths
LIBRARY_BOOKS = {
    'beginner': [
        {'title': 'The Adventures of Tom Sawyer', 'author': 'Mark Twain', 'file_path': 'libruary/beginner/The Adventures of Tom Sawyer.pdf'},
        {'title': 'Peter Pan', 'author': 'J.M. Barrie', 'file_path': 'libruary/beginner/Peter Pan.pdf'},
        {'title': 'The Last Photo', 'author': 'Unknown', 'file_path': 'libruary/beginner/The Last Photo.pdf'},
        {'title': 'Hannah and the Hurricane', 'author': 'Unknown', 'file_path': 'libruary/beginner/Hannah and the Hurricane.pdf'},
        {'title': 'Muhammad Ali', 'author': 'Unknown', 'file_path': 'libruary/beginner/Muhammad Ali.pdf'},
        {'title': 'The Boy Who Couldnt Sleep', 'author': 'Unknown', 'file_path': 'libruary/beginner/The Boy Who Couldnt Sleep.pdf'},
        {'title': 'Between Two Worlds', 'author': 'Unknown', 'file_path': 'libruary/beginner/Between_two_worlds.pdf'},
        {'title': 'Zorro', 'author': 'Unknown', 'file_path': 'libruary/beginner/Zorro.pdf'},
        {'title': 'Maisie and the Dolphin', 'author': 'Unknown', 'file_path': 'libruary/beginner/Maisie and the Dolphin.pdf'},
        {'title': 'Flying Home', 'author': 'Unknown', 'file_path': 'libruary/beginner/Flying Home .pdf'},
        {'title': 'The Three Billy Goats Gruffung', 'author': 'Unknown', 'file_path': 'libruary/beginner/The Three Billy Goats Gruffung.pdf'},
        {'title': 'Brown Eyes', 'author': 'Unknown', 'file_path': 'libruary/beginner/Brown Eyes.pdf'},
        {'title': 'San Francisco Story', 'author': 'Unknown', 'file_path': 'libruary/beginner/San Francisco Story.pdf'},
        {'title': 'Pirate Treasure', 'author': 'Phillip Burrows & Mark Foster', 'file_path': 'libruary/beginner/burrows_phillip_foster_mark_pirate_treasure_bookworms_starte.pdf'},
        {'title': 'A Connecticut Yankee in King Arthurs Court', 'author': 'Mark Twain', 'file_path': 'libruary/beginner/twain_mark_a_connecticut_yankee_in_king_arthur_s_court.pdf'},
        {'title': 'Carnival', 'author': 'Unknown', 'file_path': 'libruary/beginner/003 Carnival.pdf'},
        {'title': 'April in Moscow', 'author': 'Unknown', 'file_path': 'libruary/beginner/002 April in Moscow.pdf'},
        {'title': 'William Tell', 'author': 'Unknown', 'file_path': 'libruary/beginner/William Tell.pdf'},
        {'title': 'Drive into Danger', 'author': 'Rosemary Border', 'file_path': 'libruary/beginner/border_rosemary_drive_into_danger.pdf'},
        {'title': 'Police TV', 'author': 'Tim Vaughan', 'file_path': 'libruary/beginner/vicary_tim_police_tv.pdf'},
        {'title': 'The White Stones', 'author': 'Lester Vaughan', 'file_path': 'libruary/beginner/vaughan_lester_the_white_stones.pdf'},
        {'title': 'Taxi of Terror', 'author': 'Phillip Burrows', 'file_path': 'libruary/beginner/burrows_phillip_taxi_of_terror.pdf'},
        {'title': 'Oranges in the Snow', 'author': 'Phillip Burrows & Mark Foster', 'file_path': 'libruary/beginner/burrows_philip_foster_mark_oranges_in_the_snow.pdf'},
        {'title': 'A New Zealand Adventure', 'author': 'Unknown', 'file_path': 'libruary/beginner/A New Zealand Adventure.pdf'},
        {'title': 'Dinos Day in London', 'author': 'Unknown', 'file_path': 'libruary/beginner/Dino\'s Day in London.pdf'},
        {'title': 'Star Reporter', 'author': 'John Escott', 'file_path': 'libruary/beginner/escott_john_star_reporter.pdf'},
        {'title': 'Marcel and the White Star', 'author': 'Unknown', 'file_path': 'libruary/beginner/004 Marcel and the White Star.pdf'},
        {'title': 'The Fireboy', 'author': 'Unknown', 'file_path': 'libruary/beginner/The Fireboy.pdf'},
        {'title': 'The Pearl Girl', 'author': 'Unknown', 'file_path': 'libruary/beginner/The Pearl Girl.pdf'},
        {'title': 'Halloween Horror', 'author': 'Unknown', 'file_path': 'libruary/beginner/Halloween Horror.pdf'}
    ],
    'elementary': [
        {'title': 'The Curse of the Black Pearl', 'author': 'Unknown', 'file_path': 'libruary/Elementary/The Curse of the Black Pearl.pdf'},
        {'title': 'Five Short Plays', 'author': 'M. Ford', 'file_path': 'libruary/Elementary/ford_m_bookworms_playscripts_five_short_plays.pdf'},
        {'title': 'Robinson Crusoe', 'author': 'Daniel Defoe', 'file_path': 'libruary/Elementary/Daniel Defoe - Robinson Crusoe.pdf'},
        {'title': 'Titanic', 'author': 'Unknown', 'file_path': 'libruary/Elementary/Titanic.pdf'},
        {'title': 'Dead Mans Chest', 'author': 'Unknown', 'file_path': 'libruary/Elementary/Dead Mans Chest.pdf'},
        {'title': 'The Missing Coins', 'author': 'John Escott', 'file_path': 'libruary/Elementary/John Escott - The Missing Coins.pdf'},
        {'title': 'Kidnapped', 'author': 'Robert Louis Stevenson', 'file_path': 'libruary/Elementary/Robert Louis Stevenson - Kidnapped.pdf'},
        {'title': 'Hercules', 'author': 'Timothy Boggs', 'file_path': 'libruary/Elementary/Timothy Boggs - Hercules.pdf'},
        {'title': 'The Room in the Tower and Other Ghost Stories', 'author': 'Rudyard Kipling', 'file_path': 'libruary/Elementary/Rudyard_Kipling_The_Room_in_the_Tower_and_Other_Ghost_Stories.pdf'},
        {'title': 'Halloween', 'author': 'Unknown', 'file_path': 'libruary/Elementary/Halloween.pdf'},
        {'title': 'King Arthur and the Knights of the Round Table', 'author': 'Unknown', 'file_path': 'libruary/Elementary/King Arthur and the Knights of the Round Table.pdf'},
        {'title': 'Round the World in 80 Days', 'author': 'Jules Verne', 'file_path': 'libruary/Elementary/Jules Verne - Round the World in 80 Days.pdf'},
        {'title': 'The Secret Life of Walter Mitty', 'author': 'Unknown', 'file_path': 'libruary/Elementary/The Secret Life of Walter Mitty.pdf'},
        {'title': 'Moby Dick', 'author': 'Kathy Burke', 'file_path': 'libruary/Elementary/Kathy Burke - Moby Dick.pdf'},
        {'title': 'Robin Hood', 'author': 'Neil Philip', 'file_path': 'libruary/Elementary/Neil Philip - Robin Hood.pdf'},
        {'title': 'The Ghost of Genny Castle', 'author': 'John Escott', 'file_path': 'libruary/Elementary/John Escott - The Ghost of Genny Castle.pdf'},
        {'title': 'Newspaper Chase', 'author': 'John Escott', 'file_path': 'libruary/Elementary/John Escott - Newspaper Chase.pdf'},
        {'title': 'The Coldest Place on Earth', 'author': 'Tim Vicary', 'file_path': 'libruary/Elementary/Tim Vicary - The Coldest Place on Earth.pdf'},
        {'title': 'Mr.Bean in town', 'author': 'Richard Curtis', 'file_path': 'libruary/Elementary/Richard Curtis - Mr.Bean in town.pdf'},
        {'title': 'Alices Adventures in Wonderland', 'author': 'Lewis Carroll', 'file_path': 'libruary/Elementary/Lewis Carroll - Alice\'s Adventures in Wonderland.pdf'},
        {'title': 'Robinson Crusoe (Complete)', 'author': 'Daniel Defoe', 'file_path': 'libruary/Elementary/defoe_daniel_robinson_crusoe.pdf'},
        {'title': 'Jaws', 'author': 'Peter Benchley', 'file_path': 'libruary/Elementary/Peter Benchley - Jaws.pdf'},
        {'title': 'Les Miserables', 'author': 'Victor Hugo', 'file_path': 'libruary/Elementary/hugo_victor_les_miserables.pdf'},
        {'title': 'The Piano', 'author': 'Rosemary Border', 'file_path': 'libruary/Elementary/Rosemary Border - The Piano.pdf'},
        {'title': 'Robin Hood (Complete)', 'author': 'Unknown', 'file_path': 'libruary/Elementary/017 Robin Hood.pdf'},
        {'title': 'Return to Earth', 'author': 'Christopher John', 'file_path': 'libruary/Elementary/christopher_john_return_to_earth.pdf'},
        {'title': 'The Presidents Murderer', 'author': 'Jennifer Bassett', 'file_path': 'libruary/Elementary/bassett_jennifer_the_president_s_murderer.pdf'},
        {'title': 'London', 'author': 'John Escott', 'file_path': 'libruary/Elementary/John.Escott-London(Oxford.Bookworms.1).pdf'},
        {'title': 'The Wave', 'author': 'Unknown', 'file_path': 'libruary/Elementary/014 The Wave.pdf'},
        {'title': 'The Story of the Treasure Seekers', 'author': 'Unknown', 'file_path': 'libruary/Elementary/018 The Story of the Treasure Seekers.pdf'},
        {'title': 'Sherlock Holmes and Sport of Kings', 'author': 'Arthur Conan Doyle', 'file_path': 'libruary/Elementary/conan_doyle_arthur_sherlock_holmes_and_sport_of_kings.pdf'},
        {'title': 'Hampton House', 'author': 'Unknown', 'file_path': 'libruary/Elementary/Hampton House.pdf'}
    ],
    'pre_intermediate': [
        {'title': 'The Canterbury Tales', 'author': 'Geoffrey Chaucer', 'file_path': 'libruary/Pre-intermediate/Geoffrey Chaucer - The Canterbury Tales.pdf'},
        {'title': 'Famous British Criminals', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/Famous British Criminals.pdf'},
        {'title': 'Manchester United', 'author': 'Kevin Brophy', 'file_path': 'libruary/Pre-intermediate/Kevin Brophy - Manchester United.pdf'},
        {'title': 'African Adventure', 'author': 'Margaret Iggulden', 'file_path': 'libruary/Pre-intermediate/Margaret Iggulden - African Adventure.pdf'},
        {'title': 'Batman Begins', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/Batman Begins.pdf'},
        {'title': 'Forrest Gump', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/Forrest Gump.pdf'},
        {'title': 'The Mummy', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/The Mummy.pdf'},
        {'title': 'The Count of Monte Cristo', 'author': 'Alexander Dumas', 'file_path': 'libruary/Pre-intermediate/Alexander Dumas - The Count of Monte Cristo.pdf'},
        {'title': 'Princess Diana', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/Princess Diana.pdf'},
        {'title': 'Mr. Bean in Town', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/Mr. Bean in Town.pdf'},
        {'title': 'The Beast', 'author': 'Carolyn Walker', 'file_path': 'libruary/Pre-intermediate/Carolyn Walker - The Beast.pdf'},
        {'title': 'Hamlet', 'author': 'William Shakespeare', 'file_path': 'libruary/Pre-intermediate/William Shakespeare - Hamlet.pdf'},
        {'title': 'New York', 'author': 'Vicky Shipton', 'file_path': 'libruary/Pre-intermediate/Vicky Shipton - New York.pdf'},
        {'title': 'British Life', 'author': 'Anne Collins', 'file_path': 'libruary/Pre-intermediate/Anne Collins - British Life.pdf'},
        {'title': 'The Beatles', 'author': 'Paul Shipton', 'file_path': 'libruary/Pre-intermediate/Paul Shipton - The Beatles.pdf'},
        {'title': 'The USA', 'author': 'Alison Baxter', 'file_path': 'libruary/Pre-intermediate/Alison Baxter - The USA.pdf'},
        {'title': 'The Turn of the Screw', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/035 The Turn of the Screw.pdf'},
        {'title': 'The Ghosts of Izieu', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/034 The Ghosts of Izieu.pdf'},
        {'title': 'NY Stories', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/NY Stories.pdf'},
        {'title': 'The Count of Monte Cristo (Complete)', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/032 The Count of Monte Cristo.pdf'},
        {'title': 'The Horse Whisperer', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/033 The Horse Whisperer.pdf'},
        {'title': 'Seasons', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/seasons.pdf'},
        {'title': 'Skyjack', 'author': 'Tim Vicary', 'file_path': 'libruary/Pre-intermediate/Tim Vicary - Skyjack.pdf'},
        {'title': 'The Bronte Story', 'author': 'Tim Vicary', 'file_path': 'libruary/Pre-intermediate/vicary_tim_the_bronte_story.pdf'},
        {'title': 'The Everest Story', 'author': 'Tim Vicary', 'file_path': 'libruary/Pre-intermediate/vicary_tim_the_everest_story.pdf'},
        {'title': 'The Picture of Dorian Gray', 'author': 'Oscar Wilde', 'file_path': 'libruary/Pre-intermediate/The Picture of Dorian Gray.pdf'},
        {'title': 'The Red Badge of Courage', 'author': 'Unknown', 'file_path': 'libruary/Pre-intermediate/036 The Red Badge of Courage.pdf'}
    ],
    'intermediate': [
        {'title': 'Management Gurus', 'author': 'David Evans', 'file_path': 'libruary/Intermediate/David Evans - Management Gurus.pdf'},
        {'title': 'The Night of the Green Dragon', 'author': 'Dorothy Dixon', 'file_path': 'libruary/Intermediate/Dorothy Dixon - The Night of the Green Dragon.pdf'},
        {'title': 'King Arthur and His Knights', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/King Arthur and His Knights.pdf'},
        {'title': 'The Dream and other Stories', 'author': 'Daphne du Maurier', 'file_path': 'libruary/Intermediate/Daphne du Maurier - The Dream and other Stories.pdf'},
        {'title': 'The Murder at the Vicarage', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/The Murder at the Vicarage.pdf'},
        {'title': '6 Songs', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/6 Songs.pdf'},
        {'title': 'City of Lights', 'author': 'Tim Vicary', 'file_path': 'libruary/Intermediate/Tim Vicary - City of Lights.pdf'},
        {'title': 'Notting Hill', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/Notting Hill.pdf'},
        {'title': 'The House of Stairs', 'author': 'Barbara Vine', 'file_path': 'libruary/Intermediate/Barbara Vine - The House of Stairs.pdf'},
        {'title': 'Secret Codes', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/Secret Codes.pdf'},
        {'title': 'The Curious Case Of Benjamin Button', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/The Curious Case Of Benjamin Button.pdf'},
        {'title': 'The Hound of the Baskervilles', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/The Hound of the Baskervilles.pdf'},
        {'title': 'The Thirty-Nine Steps', 'author': 'John Buchan', 'file_path': 'libruary/Intermediate/John Buchan - The Thirty-Nine Steps.pdf'},
        {'title': 'Lorna Doone', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/056 Lorna Doone.pdf'},
        {'title': 'As Time Goes By', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/055 As Time Goes By.pdf'},
        {'title': 'Silas Marner', 'author': 'George Eliot', 'file_path': 'libruary/Intermediate/eliot_george_silas_marner.pdf'},
        {'title': 'A Tale of Two Cities', 'author': 'Charles Dickens', 'file_path': 'libruary/Intermediate/dickens_charles_a_tale_of_two_cities.pdf'},
        {'title': 'Great Crimes', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/Great_Crimes.pdf'},
        {'title': 'Primary Colors', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/057 Primary Colors.pdf'},
        {'title': 'The Prisoner of Zenda', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/The Prisoner of Zenda.pdf'},
        {'title': 'The Thirty-Nine Steps (Complete)', 'author': 'John Buchan', 'file_path': 'libruary/Intermediate/buchan_john_the_thirty_nine_steps.pdf'},
        {'title': 'Dr. Jekyll and Mr. Hyde', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/dr.jekyll  mr.hyde book.pdf'},
        {'title': 'Cinderella Man', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/054 Cinderella Man.pdf'},
        {'title': 'Strangers on a Train', 'author': 'Unknown', 'file_path': 'libruary/Intermediate/058 Strangers on a Train.pdf'},
        {'title': 'Ethan Frome', 'author': 'Edith Wharton', 'file_path': 'libruary/Intermediate/wharton_edith_ethan_frome.pdf'},
        {'title': 'Gladiator', 'author': 'Dewey Gram', 'file_path': 'libruary/Intermediate/Dewey Gram - Gladiator.pdf'}
    ],
    'upper_intermediate': [
        {'title': 'Dolphin Music', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/Dolphin Music.pdf'},
        {'title': 'History of English Language', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/History of English Language.pdf'},
        {'title': 'A Fishy Story', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/A Fishy Story.pdf'},
        {'title': 'Blood Feuds', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/Blood Feuds.pdf'},
        {'title': 'The Story of the Internet', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/The Story of the Internet.pdf'},
        {'title': 'Treading on Dreams', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/Treading on Dreams.PDF'},
        {'title': 'This Rough Magic', 'author': 'Mary Stewart', 'file_path': 'libruary/Upper-intermediate/stewart_mary_this_rough_magic_stage_5.pdf'},
        {'title': 'On the Road', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/079 On the Road.pdf'},
        {'title': 'Airport', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/077 Airport.pdf'},
        {'title': 'The Firm', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/081 The Firm.pdf'},
        {'title': 'Wuthering Heights', 'author': 'Emily Bronte', 'file_path': 'libruary/Upper-intermediate/bronte_emily_wuthering_heights.pdf'},
        {'title': 'The Great Gatsby', 'author': 'F. Scott Fitzgerald', 'file_path': 'libruary/Upper-intermediate/fitzgerald_f_scott_the_great_gatsby.pdf'},
        {'title': 'The Dead of Jericho', 'author': 'Colin Dexter', 'file_path': 'libruary/Upper-intermediate/dexter_colin_the_dead_of_jericho.pdf'},
        {'title': 'The Body', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/078 The Body.pdf'},
        {'title': 'The Age of Innocence', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/The Age of Innocence.pdf'},
        {'title': 'Pride and Prejudice', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/080 Pride and Prejudice.pdf'},
        {'title': 'The Accidental Tourist', 'author': 'Anne Tyler', 'file_path': 'libruary/Upper-intermediate/tyler_anne_the_accidental_tourist.pdf'},
        {'title': 'Sense and Sensibility', 'author': 'Jane Austen', 'file_path': 'libruary/Upper-intermediate/austen_jane_sense_and_sensibility.pdf'},
        {'title': 'The Bride Price', 'author': 'Buchi Emecheta', 'file_path': 'libruary/Upper-intermediate/emecheta_buchi_the_bride_price.pdf'},
        {'title': 'Murder by Art', 'author': 'Unknown', 'file_path': 'libruary/Upper-intermediate/Murder by Art.pdf'}
    ],
    'advanced': [
        {'title': 'Double Helix', 'author': 'Unknown', 'file_path': 'libruary/Advanced/Double Helix.pdf'},
        {'title': 'Captain Corellis Mandolin', 'author': 'Unknown', 'file_path': 'libruary/Advanced/Captain Corellis Mandolin.pdf'},
        {'title': 'Age of Dragons', 'author': 'Unknown', 'file_path': 'libruary/Advanced/Age of Dragons.pdf'},
        {'title': 'Les Miserables', 'author': 'Unknown', 'file_path': 'libruary/Advanced/Les Miserables.pdf'},
        {'title': 'The Moonstone', 'author': 'Unknown', 'file_path': 'libruary/Advanced/The Moonstone.pdf'}
    ]
}

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command with inline keyboard"""
    user_id = update.effective_user.id
    user_modes[user_id] = 'general'  # Reset to general mode
    
    welcome_message = f"""🤖 Welcome to the Education Bot!

I'm your AI-powered learning assistant. Choose a learning mode below:

Rate limit: {RATE_LIMIT_PER_USER} messages per minute"""
    
    # Create inline keyboard
    keyboard = [
        [
            InlineKeyboardButton("✍️ Writing", callback_data="writing"),
            InlineKeyboardButton("🗣️ Speaking", callback_data="speaking")
        ],
        [
            InlineKeyboardButton("📖 Reading", callback_data="reading"),
            InlineKeyboardButton("👂 Listening", callback_data="listening")
        ],
        [
            InlineKeyboardButton("🎮 Mini App", callback_data="mini_app"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="status")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_message, reply_markup=reply_markup)

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data == "writing":
        user_modes[user_id] = 'writing'
        await handle_writing_mode(query, context)
    elif query.data == "speaking":
        user_modes[user_id] = 'speaking'
        await handle_speaking_mode(query, context)
    elif query.data == "reading":
        user_modes[user_id] = 'reading'
        await handle_reading_mode(query, context)
    elif query.data == "listening":
        user_modes[user_id] = 'listening'
        await handle_listening_mode(query, context)
    elif query.data == "help":
        await handle_help_mode(query, context)
    elif query.data == "status":
        await handle_status_mode(query, context)
    elif query.data == "back_to_main":
        user_modes[user_id] = 'general'
        await show_main_menu(query, context)
    elif query.data == "library":
        await handle_library_mode(query, context)
    elif query.data.startswith("level_"):
        level = query.data.replace("level_", "")
        await handle_level_selection(query, context, level)
    elif query.data.startswith("book_"):
        book_data = query.data.replace("book_", "")
        level, book_index = book_data.split("_")
        await handle_book_selection(query, context, level, int(book_index))
    elif query.data == "back_to_reading":
        await handle_reading_mode(query, context)
    elif query.data == "back_to_library":
        await handle_library_mode(query, context)
    elif query.data == "listening_podcasts":
        await handle_listening_podcasts(query, context)
    elif query.data == "listening_movies":
        await handle_listening_movies(query, context)
    elif query.data == "listening_news":
        await handle_listening_news(query, context)
    elif query.data == "listening_audiomate":
        await handle_listening_audiomate(query, context)
    elif query.data == "back_to_listening":
        await handle_listening_mode(query, context)
    elif query.data == "mini_app":
        user_modes[user_id] = 'mini_app'
        await handle_mini_app(query, context)
    elif query.data == "back_to_miniapp":
        await handle_mini_app(query, context)
    elif query.data.startswith("vocab_"):
        await handle_vocabulary_game(query, context)
    elif query.data.startswith("grammar_"):
        await handle_grammar_quiz(query, context)
    elif query.data.startswith("word_match_"):
        await handle_word_matching(query, context)
    elif query.data.startswith("fill_blank_"):
        await handle_fill_blanks(query, context)
    elif query.data == "daily_challenge":
        await handle_daily_challenge(query, context)
    elif query.data == "progress_stats":
        await handle_progress_stats(query, context)

async def show_main_menu(query, context):
    """Show the main menu"""
    user_id = query.from_user.id
    user_modes[user_id] = 'general'
    
    welcome_message = f"""🤖 Welcome to the Education Bot!

I'm your AI-powered learning assistant. Choose a learning mode below:

Rate limit: {RATE_LIMIT_PER_USER} messages per minute"""
    
    keyboard = [
        [
            InlineKeyboardButton("✍️ Writing", callback_data="writing"),
            InlineKeyboardButton("🗣️ Speaking", callback_data="speaking")
        ],
        [
            InlineKeyboardButton("📖 Reading", callback_data="reading"),
            InlineKeyboardButton("👂 Listening", callback_data="listening")
        ],
        [
            InlineKeyboardButton("🎮 Mini App", callback_data="mini_app"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help")
        ],
        [
            InlineKeyboardButton("📊 Status", callback_data="status")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(welcome_message, reply_markup=reply_markup)

async def handle_writing_mode(query, context):
    """Handle writing mode"""
    message = """✍️ **Writing Mode**

Send me any text and I'll help you with:
• Grammar corrections
• Writing suggestions
• Essay structure
• Creative writing ideas
• Academic writing tips

Just type your message below!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_speaking_mode(query, context):
    """Handle speaking mode"""
    message = """🗣️ **Speaking Mode**

Send me voice messages and I'll help you with:
• Pronunciation feedback
• Speaking practice
• Conversation starters
• Public speaking tips
• Language learning

Send a voice message or type your text!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_reading_mode(query, context):
    """Handle reading mode"""
    message = """📖 **Reading Mode**

Choose what you'd like to do:

• Send me text for reading comprehension help
• Access our digital library with books for all levels
• Get vocabulary and analysis assistance
• Discuss literature and reading strategies

What would you like to do?"""
    
    keyboard = [
        [InlineKeyboardButton("📚 Digital Library", callback_data="library")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_library_mode(query, context):
    """Handle library mode"""
    message = """📚 **Digital Library**

Choose your reading level:

• **Beginner**: Simple stories, basic vocabulary
• **Elementary**: Short novels, everyday language
• **Pre-intermediate**: Young adult books, clear plots
• **Intermediate**: Classic literature, moderate complexity
• **Upper-intermediate**: Advanced classics, rich vocabulary
• **Advanced**: Complex literature, sophisticated themes

Select your level to see available books:"""
    
    keyboard = [
        [
            InlineKeyboardButton("🟢 Beginner", callback_data="level_beginner"),
            InlineKeyboardButton("🟡 Elementary", callback_data="level_elementary")
        ],
        [
            InlineKeyboardButton("🟠 Pre-intermediate", callback_data="level_pre_intermediate"),
            InlineKeyboardButton("🔵 Intermediate", callback_data="level_intermediate")
        ],
        [
            InlineKeyboardButton("🟣 Upper-intermediate", callback_data="level_upper_intermediate"),
            InlineKeyboardButton("🔴 Advanced", callback_data="level_advanced")
        ],
        [InlineKeyboardButton("🔙 Back to Reading", callback_data="back_to_reading")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_level_selection(query, context, level):
    """Handle level selection and show books"""
    books = LIBRARY_BOOKS.get(level, [])
    
    if not books:
        message = "No books available for this level yet. Please check back later!"
        keyboard = [[InlineKeyboardButton("🔙 Back to Library", callback_data="back_to_library")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(message, reply_markup=reply_markup)
        return
    
    level_names = {
        'beginner': 'Beginner',
        'elementary': 'Elementary', 
        'pre_intermediate': 'Pre-intermediate',
        'intermediate': 'Intermediate',
        'upper_intermediate': 'Upper-intermediate',
        'advanced': 'Advanced'
    }
    
    message = f"""📚 **{level_names[level]} Level Books**

Available books for your level:"""
    
    keyboard = []
    for i, book in enumerate(books):
        keyboard.append([InlineKeyboardButton(
            f"📖 {book['title']} - {book['author']}", 
            callback_data=f"book_{level}_{i}"
        )])
    
    keyboard.append([InlineKeyboardButton("🔙 Back to Library", callback_data="back_to_library")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_book_selection(query, context, level, book_index):
    """Handle book selection and send PDF"""
    books = LIBRARY_BOOKS.get(level, [])
    
    if book_index >= len(books):
        await query.answer("Book not found!")
        return
    
    book = books[book_index]
    
    message = f"""📖 **{book['title']}**
👤 **Author:** {book['author']}
📚 **Level:** {level.replace('_', ' ').title()}

Here's your book! Enjoy reading! 📖✨"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Library", callback_data="back_to_library")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # Send the message first
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    # Check if the PDF file exists
    file_path = book['file_path']
    
    if os.path.exists(file_path):
        try:
            # Send the actual PDF file from local storage
            with open(file_path, 'rb') as pdf_file:
                await context.bot.send_document(
                    chat_id=query.message.chat_id,
                    document=pdf_file,
                    filename=f"{book['title'].replace(' ', '_')}.pdf",
                    caption=f"📖 {book['title']} by {book['author']}\n📚 Level: {level.replace('_', ' ').title()}"
                )
        except Exception as error:
            logger.error(f'Error sending PDF for book {book["title"]}: {error}')
            # Fallback message if PDF sending fails
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=f"❌ Sorry, there was an error sending the PDF for '{book['title']}'. Please try again later or contact support.",
                parse_mode='Markdown'
            )
    else:
        # Send a message if PDF file doesn't exist
        await context.bot.send_message(
            chat_id=query.message.chat_id,
            text=f"""📖 **{book['title']}** by {book['author']}
📚 **Level:** {level.replace('_', ' ').title()}

📄 **PDF Status:** File not found
📁 **Expected path:** `{file_path}`

🔧 **To add this PDF:**
1. Create the folder structure: `pdfs/{level}/`
2. Add the PDF file: `{os.path.basename(file_path)}`
3. Restart the bot

For now, you can find this book online or in your local library! 📚""",
            parse_mode='Markdown'
        )

async def handle_listening_mode(query, context):
    """Handle listening mode"""
    message = """👂 **Listening Mode**

Choose your listening practice:"""
    
    keyboard = [
        [InlineKeyboardButton("🎧 Podcasts", callback_data="listening_podcasts")],
        [InlineKeyboardButton("🎬 Movies & TV Shows", callback_data="listening_movies")],
        [InlineKeyboardButton("📺 News Videos / TED Talks / YouTube Channels", callback_data="listening_news")],
        [InlineKeyboardButton("👂AudioMate", callback_data="listening_audiomate")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_listening_podcasts(query, context):
    """Handle podcast listening mode"""
    message = """🎧 **Podcasts for English Learning**

Here are some recommended podcasts to improve your English listening skills:

🎙️ **Joe Rogan Experience**
https://www.youtube.com/@joerogan

🎙️ **Lex Fridman Podcast**
https://www.youtube.com/@lexfridman

🎙️ **BBC Learning English**
https://www.youtube.com/@bbclearningenglish

🎙️ **A.J. Hoge - Effortless English**
https://www.youtube.com/@AJHogeEffortlessEnglish

🎙️ **Veronika's Language Diaries**
https://www.youtube.com/@veronikas.languagediaries

🎙️ **Silicon Valley Girl**
https://www.youtube.com/@SiliconValleyGirl

These podcasts will help you:
• Improve listening comprehension
• Learn natural conversation patterns
• Expand vocabulary
• Practice different accents and speaking styles"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Listening", callback_data="back_to_listening")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_listening_movies(query, context):
    """Handle movies and TV shows listening mode"""
    message = """🎬 **Movies & TV Shows for English Learning**

Great series and movies to improve your English:

📺 **TV Series:**
• Friends
• Breaking Bad
• Riverdale
• Vikings
• Stranger Things
• Suits
• Succession
• Better Call Saul
• The Sopranos
• Attack on Titans
• Game of Thrones
• The Office
• Gravity Falls

🎬 **Movies:**
• All Avengers parts
• Watchmen
• All Guardians of the Galaxy parts
• Moneyball
• The Founder
• All GodFather parts
• The Lord of The Rings
• Schindler's List
• Pulp Fiction
• Forrest Gump
• Fight Club
• Interstellar
• The Green Mile
• Green Book
• City of God
• Back to the Future
• Gladiator

🎭 **Where to watch:**
Check out this collection: https://rezka.ag/films/best/

These will help you:
• Learn conversational English
• Understand cultural references
• Improve pronunciation
• Practice different dialects"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Listening", callback_data="back_to_listening")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_listening_news(query, context):
    """Handle news videos and educational content"""
    message = """📺 **News Videos / TED Talks / YouTube Channels**

Enhance your English with educational content:

🎥 **Platform:** YouTube
https://www.youtube.com/

**Recommended Content Types:**
• 🗞️ News channels (BBC, CNN, etc.)
• 🎯 TED Talks for inspiration and learning
• 📚 Educational YouTube channels
• 🌍 Documentary channels
• 💼 Business and technology content

**Benefits:**
• Learn formal English
• Stay updated with current events
• Improve academic vocabulary
• Practice listening to different speakers
• Understand various topics and contexts

**Tips for Learning:**
• Use subtitles initially, then try without
• Take notes of new vocabulary
• Pause and replay difficult sections
• Discuss what you learned"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Listening", callback_data="back_to_listening")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_listening_audiomate(query, context):
    """Handle AudioMate - original audio processing functionality"""
    message = """👂 **AudioMate**

Send me audio files and I'll help you with:
• Audio transcription
• Listening comprehension
• Audio analysis
• Note-taking from audio
• Podcast discussions

Send an audio file or ask about listening skills!"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Listening", callback_data="back_to_listening")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

# Store user progress and game data
user_progress = {}
user_game_data = {}

# Vocabulary data for games
VOCABULARY_DATA = {
    'beginner': [
        {'word': 'cat', 'definition': 'A small domesticated carnivorous mammal', 'example': 'The cat is sleeping on the sofa.'},
        {'word': 'house', 'definition': 'A building for human habitation', 'example': 'I live in a big house.'},
        {'word': 'book', 'definition': 'A written or printed work consisting of pages', 'example': 'I am reading a good book.'},
        {'word': 'water', 'definition': 'A colorless, transparent, odorless liquid', 'example': 'I drink water every day.'},
        {'word': 'happy', 'definition': 'Feeling or showing pleasure or contentment', 'example': 'She looks very happy today.'},
    ],
    'intermediate': [
        {'word': 'perseverance', 'definition': 'Persistence in doing something despite difficulty', 'example': 'Her perseverance helped her achieve success.'},
        {'word': 'magnificent', 'definition': 'Impressively beautiful, elaborate, or extravagant', 'example': 'The view from the mountain was magnificent.'},
        {'word': 'collaborate', 'definition': 'Work jointly on an activity', 'example': 'We need to collaborate to finish this project.'},
        {'word': 'ambitious', 'definition': 'Having a strong desire for success or achievement', 'example': 'He is an ambitious young entrepreneur.'},
        {'word': 'inevitable', 'definition': 'Certain to happen; unavoidable', 'example': 'Change is inevitable in life.'},
    ],
    'advanced': [
        {'word': 'serendipity', 'definition': 'The occurrence of events by chance in a happy way', 'example': 'Meeting my mentor was pure serendipity.'},
        {'word': 'ubiquitous', 'definition': 'Present, appearing, or found everywhere', 'example': 'Smartphones are ubiquitous in modern society.'},
        {'word': 'ephemeral', 'definition': 'Lasting for a very short time', 'example': 'The beauty of cherry blossoms is ephemeral.'},
        {'word': 'quintessential', 'definition': 'Representing the most perfect example of a quality', 'example': 'He is the quintessential gentleman.'},
        {'word': 'perspicacious', 'definition': 'Having keen insight; shrewd', 'example': 'Her perspicacious analysis impressed everyone.'},
    ]
}

GRAMMAR_QUESTIONS = [
    {
        'question': 'Choose the correct form: "She ___ to the store yesterday."',
        'options': ['go', 'goes', 'went', 'going'],
        'correct': 2,
        'explanation': '"Went" is the past tense of "go" and matches with "yesterday".'
    },
    {
        'question': 'Which is correct: "I have ___ this movie before."',
        'options': ['see', 'saw', 'seen', 'seeing'],
        'correct': 2,
        'explanation': '"Seen" is used with "have" in present perfect tense.'
    },
    {
        'question': 'Complete: "If it ___ tomorrow, we will stay home."',
        'options': ['rain', 'rains', 'rained', 'raining'],
        'correct': 1,
        'explanation': 'First conditional uses present simple in the if-clause.'
    },
    {
        'question': 'Choose correct: "She is good ___ mathematics."',
        'options': ['in', 'at', 'on', 'with'],
        'correct': 1,
        'explanation': 'We use "good at" for skills and abilities.'
    },
    {
        'question': 'Which is right: "There ___ many people at the party."',
        'options': ['was', 'were', 'is', 'are'],
        'correct': 1,
        'explanation': '"Were" is used with plural subjects in past tense.'
    }
]

WORD_PAIRS = [
    {'english': 'Happy', 'synonym': 'Joyful'},
    {'english': 'Big', 'synonym': 'Large'},
    {'english': 'Smart', 'synonym': 'Intelligent'},
    {'english': 'Fast', 'synonym': 'Quick'},
    {'english': 'Beautiful', 'synonym': 'Gorgeous'},
    {'english': 'Difficult', 'synonym': 'Challenging'},
    {'english': 'Important', 'synonym': 'Significant'},
    {'english': 'Angry', 'synonym': 'Furious'},
]

FILL_BLANK_SENTENCES = [
    {
        'sentence': 'The weather is very ___ today.',
        'options': ['nice', 'book', 'run', 'water'],
        'correct': 0,
        'hint': 'Think about describing weather positively.'
    },
    {
        'sentence': 'I need to ___ my homework before dinner.',
        'options': ['eat', 'finish', 'sleep', 'walk'],
        'correct': 1,
        'hint': 'What do you do with homework?'
    },
    {
        'sentence': 'She ___ a beautiful song at the concert.',
        'options': ['danced', 'painted', 'sang', 'wrote'],
        'correct': 2,
        'hint': 'What do you do with songs at concerts?'
    },
    {
        'sentence': 'The ___ is shining brightly in the sky.',
        'options': ['moon', 'sun', 'star', 'cloud'],
        'correct': 1,
        'hint': 'What gives us light during the day?'
    }
]

async def handle_mini_app(query, context):
    """Handle mini app main menu"""
    user_id = query.from_user.id
    
    # Initialize user progress if not exists
    if user_id not in user_progress:
        user_progress[user_id] = {
            'vocab_score': 0,
            'grammar_score': 0,
            'games_played': 0,
            'streak_days': 0,
            'level': 'beginner'
        }
    
    message = """🎮 **Learning Mini App**

Welcome to your interactive English learning playground! Choose an activity to boost your skills:

🎯 **Your Progress:**
• Vocabulary Score: {vocab_score}
• Grammar Score: {grammar_score}
• Games Played: {games_played}
• Current Level: {level}

🚀 **Ready to learn and have fun?**""".format(**user_progress[user_id])
    
    keyboard = [
        [
            InlineKeyboardButton("📚 Vocabulary Quiz", callback_data="vocab_quiz"),
            InlineKeyboardButton("📝 Grammar Challenge", callback_data="grammar_quiz")
        ],
        [
            InlineKeyboardButton("🎯 Word Matching", callback_data="word_match_start"),
            InlineKeyboardButton("✏️ Fill the Blanks", callback_data="fill_blank_start")
        ],
        [
            InlineKeyboardButton("🏆 Daily Challenge", callback_data="daily_challenge"),
            InlineKeyboardButton("📊 Progress Stats", callback_data="progress_stats")
        ],
        [
            InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_vocabulary_game(query, context):
    """Handle vocabulary quiz game"""
    user_id = query.from_user.id
    action = query.data.replace("vocab_", "")
    
    if action == "quiz":
        # Start new vocabulary quiz
        level = user_progress.get(user_id, {}).get('level', 'beginner')
        vocab_list = VOCABULARY_DATA.get(level, VOCABULARY_DATA['beginner'])
        
        # Select random word
        import random
        word_data = random.choice(vocab_list)
        
        # Store current question
        user_game_data[user_id] = {
            'game_type': 'vocab',
            'current_word': word_data,
            'score': 0,
            'question_count': 1,
            'total_questions': 5
        }
        
        # Create options (correct definition + 3 wrong ones)
        all_definitions = []
        for vocab_level in VOCABULARY_DATA.values():
            all_definitions.extend([v['definition'] for v in vocab_level])
        
        wrong_definitions = [d for d in all_definitions if d != word_data['definition']]
        options = [word_data['definition']] + random.sample(wrong_definitions, 3)
        random.shuffle(options)
        
        correct_index = options.index(word_data['definition'])
        user_game_data[user_id]['correct_answer'] = correct_index
        user_game_data[user_id]['options'] = options
        
        message = f"""📚 **Vocabulary Quiz** (Question 1/5)

**Word:** `{word_data['word'].upper()}`

**Choose the correct definition:**"""
        
        keyboard = []
        for i, option in enumerate(options):
            keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option[:50]}...", callback_data=f"vocab_answer_{i}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif action.startswith("answer_"):
        # Handle quiz answer
        selected = int(action.replace("answer_", ""))
        game_data = user_game_data.get(user_id, {})
        
        if not game_data:
            await query.answer("Game session expired. Please start a new quiz.")
            return
        
        correct_answer = game_data['correct_answer']
        is_correct = selected == correct_answer
        
        if is_correct:
            game_data['score'] += 1
            result_text = "✅ Correct!"
        else:
            result_text = f"❌ Wrong! The correct answer was: {game_data['options'][correct_answer]}"
        
        # Show example
        example_text = f"\n\n💡 **Example:** {game_data['current_word']['example']}"
        
        if game_data['question_count'] < game_data['total_questions']:
            # Continue to next question
            await query.answer(result_text)
            game_data['question_count'] += 1
            
            # Get next word
            level = user_progress.get(user_id, {}).get('level', 'beginner')
            vocab_list = VOCABULARY_DATA.get(level, VOCABULARY_DATA['beginner'])
            import random
            word_data = random.choice(vocab_list)
            game_data['current_word'] = word_data
            
            # Create new options
            all_definitions = []
            for vocab_level in VOCABULARY_DATA.values():
                all_definitions.extend([v['definition'] for v in vocab_level])
            
            wrong_definitions = [d for d in all_definitions if d != word_data['definition']]
            options = [word_data['definition']] + random.sample(wrong_definitions, 3)
            random.shuffle(options)
            
            correct_index = options.index(word_data['definition'])
            game_data['correct_answer'] = correct_index
            game_data['options'] = options
            
            message = f"""📚 **Vocabulary Quiz** (Question {game_data['question_count']}/5)

{result_text}{example_text}

**Word:** `{word_data['word'].upper()}`

**Choose the correct definition:**"""
            
            keyboard = []
            for i, option in enumerate(options):
                keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option[:50]}...", callback_data=f"vocab_answer_{i}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            # Quiz completed
            final_score = game_data['score']
            user_progress[user_id]['vocab_score'] += final_score
            user_progress[user_id]['games_played'] += 1
            
            # Level up logic
            if user_progress[user_id]['vocab_score'] >= 20 and user_progress[user_id]['level'] == 'beginner':
                user_progress[user_id]['level'] = 'intermediate'
                level_up_text = "\n🎉 **LEVEL UP!** You're now at Intermediate level!"
            elif user_progress[user_id]['vocab_score'] >= 50 and user_progress[user_id]['level'] == 'intermediate':
                user_progress[user_id]['level'] = 'advanced'
                level_up_text = "\n🎉 **LEVEL UP!** You're now at Advanced level!"
            else:
                level_up_text = ""
            
            message = f"""🎯 **Quiz Complete!**

{result_text}{example_text}

**Final Score:** {final_score}/5
**Total Vocabulary Score:** {user_progress[user_id]['vocab_score']}
{level_up_text}

Great job! Keep practicing to improve your vocabulary! 📚✨"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Play Again", callback_data="vocab_quiz")],
                [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Clear game data
            if user_id in user_game_data:
                del user_game_data[user_id]

async def handle_grammar_quiz(query, context):
    """Handle grammar quiz game"""
    user_id = query.from_user.id
    action = query.data.replace("grammar_", "")
    
    if action == "quiz":
        # Start new grammar quiz
        import random
        question_data = random.choice(GRAMMAR_QUESTIONS)
        
        # Store current question
        user_game_data[user_id] = {
            'game_type': 'grammar',
            'current_question': question_data,
            'score': 0,
            'question_count': 1,
            'total_questions': 3
        }
        
        message = f"""📝 **Grammar Challenge** (Question 1/3)

{question_data['question']}

**Choose the correct answer:**"""
        
        keyboard = []
        for i, option in enumerate(question_data['options']):
            keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"grammar_answer_{i}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif action.startswith("answer_"):
        # Handle quiz answer
        selected = int(action.replace("answer_", ""))
        game_data = user_game_data.get(user_id, {})
        
        if not game_data:
            await query.answer("Game session expired. Please start a new quiz.")
            return
        
        correct_answer = game_data['current_question']['correct']
        is_correct = selected == correct_answer
        
        if is_correct:
            game_data['score'] += 1
            result_text = "✅ Correct!"
        else:
            result_text = f"❌ Wrong! The correct answer was: {game_data['current_question']['options'][correct_answer]}"
        
        explanation = f"\n\n💡 **Explanation:** {game_data['current_question']['explanation']}"
        
        if game_data['question_count'] < game_data['total_questions']:
            # Continue to next question
            await query.answer(result_text)
            game_data['question_count'] += 1
            
            # Get next question
            import random
            question_data = random.choice(GRAMMAR_QUESTIONS)
            game_data['current_question'] = question_data
            
            message = f"""📝 **Grammar Challenge** (Question {game_data['question_count']}/3)

{result_text}{explanation}

{question_data['question']}

**Choose the correct answer:**"""
            
            keyboard = []
            for i, option in enumerate(question_data['options']):
                keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"grammar_answer_{i}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            # Quiz completed
            final_score = game_data['score']
            user_progress[user_id]['grammar_score'] += final_score
            user_progress[user_id]['games_played'] += 1
            
            message = f"""🎯 **Grammar Challenge Complete!**

{result_text}{explanation}

**Final Score:** {final_score}/3
**Total Grammar Score:** {user_progress[user_id]['grammar_score']}

Excellent work! Grammar is the foundation of good English! 📝✨"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Try Again", callback_data="grammar_quiz")],
                [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Clear game data
            if user_id in user_game_data:
                del user_game_data[user_id]

async def handle_word_matching(query, context):
    """Handle word matching game"""
    user_id = query.from_user.id
    action = query.data.replace("word_match_", "")
    
    if action == "start":
        # Start word matching game
        import random
        pairs = random.sample(WORD_PAIRS, 4)  # Select 4 pairs
        
        # Create shuffled options
        words = [(pair['english'], 'english') for pair in pairs] + [(pair['synonym'], 'synonym') for pair in pairs]
        random.shuffle(words)
        
        user_game_data[user_id] = {
            'game_type': 'word_match',
            'pairs': pairs,
            'words': words,
            'selected': [],
            'matched': [],
            'score': 0
        }
        
        message = """🎯 **Word Matching Game**

Match the synonyms! Select two words that have similar meanings.

**Instructions:**
1. Click on a word to select it
2. Click on its synonym to make a match
3. Match all 4 pairs to win!

**Words to match:**"""
        
        keyboard = []
        row = []
        for i, (word, word_type) in enumerate(words):
            if i % 2 == 0 and i > 0:
                keyboard.append(row)
                row = []
            row.append(InlineKeyboardButton(f"{word}", callback_data=f"word_match_select_{i}"))
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif action.startswith("select_"):
        # Handle word selection
        selected_index = int(action.replace("select_", ""))
        game_data = user_game_data.get(user_id, {})
        
        if not game_data or selected_index in game_data['matched']:
            await query.answer("Word already matched or game not found!")
            return
        
        if selected_index in game_data['selected']:
            # Deselect word
            game_data['selected'].remove(selected_index)
            await query.answer("Word deselected")
        else:
            # Select word
            game_data['selected'].append(selected_index)
            
            if len(game_data['selected']) == 2:
                # Check if it's a match
                word1_idx, word2_idx = game_data['selected']
                word1, type1 = game_data['words'][word1_idx]
                word2, type2 = game_data['words'][word2_idx]
                
                # Check if they form a pair
                is_match = False
                for pair in game_data['pairs']:
                    if (word1 == pair['english'] and word2 == pair['synonym']) or \
                       (word1 == pair['synonym'] and word2 == pair['english']):
                        is_match = True
                        break
                
                if is_match:
                    game_data['matched'].extend(game_data['selected'])
                    game_data['score'] += 1
                    await query.answer("✅ Great match!")
                else:
                    await query.answer("❌ Not a match, try again!")
                
                game_data['selected'] = []
                
                # Check if game is complete
                if len(game_data['matched']) == len(game_data['words']):
                    user_progress[user_id]['games_played'] += 1
                    user_progress[user_id]['vocab_score'] += game_data['score']
                    
                    message = f"""🎉 **Congratulations!**

You matched all pairs correctly!

**Score:** {game_data['score']}/4
**Total Games Played:** {user_progress[user_id]['games_played']}

Your vocabulary skills are improving! 🌟"""
                    
                    keyboard = [
                        [InlineKeyboardButton("🔄 Play Again", callback_data="word_match_start")],
                        [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
                    ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
                    
                    # Clear game data
                    if user_id in user_game_data:
                        del user_game_data[user_id]
                    return
        
        # Update display
        message = """🎯 **Word Matching Game**

Match the synonyms! Select two words that have similar meanings.

**Selected:** """ + (", ".join([game_data['words'][i][0] for i in game_data['selected']]) if game_data['selected'] else "None") + f"""
**Matches Found:** {len(game_data['matched'])//2}/4

**Words to match:**"""
        
        keyboard = []
        row = []
        for i, (word, word_type) in enumerate(game_data['words']):
            if i % 2 == 0 and i > 0:
                keyboard.append(row)
                row = []
            
            if i in game_data['matched']:
                button_text = f"✅ {word}"
            elif i in game_data['selected']:
                button_text = f"🔸 {word}"
            else:
                button_text = word
            
            row.append(InlineKeyboardButton(button_text, callback_data=f"word_match_select_{i}"))
        if row:
            keyboard.append(row)
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_fill_blanks(query, context):
    """Handle fill in the blanks game"""
    user_id = query.from_user.id
    action = query.data.replace("fill_blank_", "")
    
    if action == "start":
        # Start fill in the blanks game
        import random
        sentence_data = random.choice(FILL_BLANK_SENTENCES)
        
        user_game_data[user_id] = {
            'game_type': 'fill_blank',
            'current_sentence': sentence_data,
            'score': 0,
            'question_count': 1,
            'total_questions': 3
        }
        
        message = f"""✏️ **Fill in the Blanks** (Question 1/3)

Complete the sentence by choosing the correct word:

**"{sentence_data['sentence']}"**

💡 **Hint:** {sentence_data['hint']}"""
        
        keyboard = []
        for i, option in enumerate(sentence_data['options']):
            keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"fill_blank_answer_{i}")])
        
        keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    
    elif action.startswith("answer_"):
        # Handle answer
        selected = int(action.replace("answer_", ""))
        game_data = user_game_data.get(user_id, {})
        
        if not game_data:
            await query.answer("Game session expired. Please start a new game.")
            return
        
        correct_answer = game_data['current_sentence']['correct']
        is_correct = selected == correct_answer
        
        if is_correct:
            game_data['score'] += 1
            result_text = "✅ Perfect!"
        else:
            result_text = f"❌ Not quite! The correct answer was: {game_data['current_sentence']['options'][correct_answer]}"
        
        # Show completed sentence
        completed_sentence = game_data['current_sentence']['sentence'].replace('___', f"**{game_data['current_sentence']['options'][correct_answer]}**")
        
        if game_data['question_count'] < game_data['total_questions']:
            # Continue to next question
            await query.answer(result_text)
            game_data['question_count'] += 1
            
            # Get next sentence
            import random
            sentence_data = random.choice(FILL_BLANK_SENTENCES)
            game_data['current_sentence'] = sentence_data
            
            message = f"""✏️ **Fill in the Blanks** (Question {game_data['question_count']}/3)

{result_text}
**Complete sentence:** "{completed_sentence}"

**New sentence:**
"{sentence_data['sentence']}"

💡 **Hint:** {sentence_data['hint']}"""
            
            keyboard = []
            for i, option in enumerate(sentence_data['options']):
                keyboard.append([InlineKeyboardButton(f"{chr(65+i)}. {option}", callback_data=f"fill_blank_answer_{i}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
        else:
            # Game completed
            final_score = game_data['score']
            user_progress[user_id]['grammar_score'] += final_score
            user_progress[user_id]['games_played'] += 1
            
            message = f"""🎯 **Fill in the Blanks Complete!**

{result_text}
**Complete sentence:** "{completed_sentence}"

**Final Score:** {final_score}/3
**Total Grammar Score:** {user_progress[user_id]['grammar_score']}

Great job completing the sentences! 📝✨"""
            
            keyboard = [
                [InlineKeyboardButton("🔄 Play Again", callback_data="fill_blank_start")],
                [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
            
            # Clear game data
            if user_id in user_game_data:
                del user_game_data[user_id]

async def handle_daily_challenge(query, context):
    """Handle daily challenge"""
    user_id = query.from_user.id
    
    # Simple daily challenge - mixed mini quiz
    import random
    challenge_type = random.choice(['vocab', 'grammar', 'word_match'])
    
    if challenge_type == 'vocab':
        message = """🏆 **Daily Challenge - Vocabulary Master**

Today's challenge: Score 4/5 on a vocabulary quiz to earn bonus points!

**Reward:** +5 bonus points
**Current streak:** {} days""".format(user_progress.get(user_id, {}).get('streak_days', 0))
        
        keyboard = [
            [InlineKeyboardButton("🎯 Accept Challenge", callback_data="vocab_quiz")],
            [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
        ]
    elif challenge_type == 'grammar':
        message = """🏆 **Daily Challenge - Grammar Expert**

Today's challenge: Get perfect score on grammar quiz to earn bonus points!

**Reward:** +3 bonus points
**Current streak:** {} days""".format(user_progress.get(user_id, {}).get('streak_days', 0))
        
        keyboard = [
            [InlineKeyboardButton("🎯 Accept Challenge", callback_data="grammar_quiz")],
            [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
        ]
    else:
        message = """🏆 **Daily Challenge - Matching Master**

Today's challenge: Complete word matching game without mistakes!

**Reward:** +4 bonus points
**Current streak:** {} days""".format(user_progress.get(user_id, {}).get('streak_days', 0))
        
        keyboard = [
            [InlineKeyboardButton("🎯 Accept Challenge", callback_data="word_match_start")],
            [InlineKeyboardButton("🔙 Back to Mini App", callback_data="back_to_miniapp")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_progress_stats(query, context):
    """Handle progress statistics"""
    user_id = query.from_user.id
    stats = user_progress.get(user_id, {
        'vocab_score': 0,
        'grammar_score': 0,
        'games_played': 0,
        'streak_days': 0,
        'level': 'beginner'
    })
    
    total_score = stats['vocab_score'] + stats['grammar_score']
    
    # Calculate achievements
    achievements = []
    if stats['games_played'] >= 10:
        achievements.append("🎮 Game Master (10+ games)")
    if stats['vocab_score'] >= 25:
        achievements.append("📚 Vocabulary Expert (25+ vocab points)")
    if stats['grammar_score'] >= 15:
        achievements.append("📝 Grammar Guru (15+ grammar points)")
    if stats['level'] == 'advanced':
        achievements.append("🎓 Advanced Learner")
    
    if not achievements:
        achievements.append("🌱 Just Getting Started!")
    
    message = f"""📊 **Your Learning Progress**

🎯 **Scores:**
• Vocabulary: {stats['vocab_score']} points
• Grammar: {stats['grammar_score']} points
• Total Score: {total_score} points

🎮 **Activity:**
• Games Played: {stats['games_played']}
• Current Level: {stats['level'].title()}
• Streak: {stats['streak_days']} days

🏆 **Achievements:**
{chr(10).join(achievements)}

**Next Goal:**
• Play more games to unlock new achievements!
• Reach higher scores to level up!

Keep learning and improving! 🌟"""
    
    keyboard = [
        [InlineKeyboardButton("🎮 Play More Games", callback_data="back_to_miniapp")],
        [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_help_mode(query, context):
    """Handle help mode"""
    help_message = f"""📚 **Education Bot Help**

**Learning Modes:**
• ✍️ **Writing**: Grammar, essays, creative writing
• 🗣️ **Speaking**: Pronunciation, conversation practice
• 📖 **Reading**: Comprehension, analysis, vocabulary + Digital Library
• 👂 **Listening**: Audio transcription, comprehension

**Digital Library Features:**
• 6 reading levels (Beginner to Advanced)
• Classic and modern literature
• PDF downloads available
• Level-appropriate book selection

**How to Use:**
1. Choose a learning mode
2. Send text, voice, or audio messages
3. Get AI-powered feedback and assistance
4. Access the digital library for reading practice

**Rate Limits:**
• {RATE_LIMIT_PER_USER} messages per minute per user
• Use /status to check your limit

**Commands:**
• /start - Show main menu
• /help - Show this help
• /status - Check rate limit status"""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(help_message, reply_markup=reply_markup, parse_mode='Markdown')

async def handle_status_mode(query, context):
    """Handle status mode"""
    user_id = query.from_user.id
    remaining = rate_limiter.get_remaining_requests(user_id)
    time_until_reset = rate_limiter.get_time_until_reset(user_id)
    
    status_message = f"""📊 **Rate Limit Status**

**Remaining requests:** {remaining}/{RATE_LIMIT_PER_USER}
**Time until reset:** {int(time_until_reset / 1000)} seconds

You can send {remaining} more messages in this time window."""
    
    keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text(status_message, reply_markup=reply_markup, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await start_command(update, context)

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /status command"""
    user_id = update.effective_user.id
    remaining = rate_limiter.get_remaining_requests(user_id)
    time_until_reset = rate_limiter.get_time_until_reset(user_id)
    
    status_message = f"""📊 **Rate Limit Status**

**Remaining requests:** {remaining}/{RATE_LIMIT_PER_USER}
**Time until reset:** {int(time_until_reset / 1000)} seconds

You can send {remaining} more messages in this time window."""
    
    await update.message.reply_text(status_message, parse_mode='Markdown')

async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages"""
    user_id = update.effective_user.id
    message = update.message.text
    
    # Get current mode for user
    current_mode = user_modes.get(user_id, 'general')
    
    try:
        # Check rate limit
        if rate_limiter.is_rate_limited(user_id):
            time_until_reset = rate_limiter.get_time_until_reset(user_id)
            await update.message.reply_text(
                f"⚠️ Rate limit exceeded! Please wait {int(time_until_reset / 1000)} seconds before sending another message."
            )
            return
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Process message with Gemini using current mode
        response = await gemini_service.process_message(message, mode=current_mode)
        
        # Send response with back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, reply_markup=reply_markup)
        
    except Exception as error:
        logger.error(f'Error processing text message: {error}')
        await update.message.reply_text('❌ Sorry, I encountered an error processing your message. Please try again later.')

async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle voice messages"""
    user_id = update.effective_user.id
    voice = update.message.voice
    
    # Get current mode for user
    current_mode = user_modes.get(user_id, 'general')
    
    try:
        # Check rate limit
        if rate_limiter.is_rate_limited(user_id):
            time_until_reset = rate_limiter.get_time_until_reset(user_id)
            await update.message.reply_text(
                f"⚠️ Rate limit exceeded! Please wait {int(time_until_reset / 1000)} seconds before sending another message."
            )
            return
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Process voice message
        transcription = await voice_service.process_voice_message(voice, context.bot)
        
        # Send transcription with back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(transcription, reply_markup=reply_markup)
        
    except Exception as error:
        logger.error(f'Error processing voice message: {error}')
        await update.message.reply_text('❌ Sorry, I encountered an error processing your voice message. Please try again later.')

async def handle_audio_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle audio messages"""
    user_id = update.effective_user.id
    audio = update.message.audio
    
    # Get current mode for user
    current_mode = user_modes.get(user_id, 'general')
    
    try:
        # Check rate limit
        if rate_limiter.is_rate_limited(user_id):
            time_until_reset = rate_limiter.get_time_until_reset(user_id)
            await update.message.reply_text(
                f"⚠️ Rate limit exceeded! Please wait {int(time_until_reset / 1000)} seconds before sending another message."
            )
            return
        
        # Send typing indicator
        await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
        
        # Process audio message (treat as voice for now)
        transcription = await voice_service.process_voice_message(audio, context.bot)
        
        # Send transcription with back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(transcription, reply_markup=reply_markup)
        
    except Exception as error:
        logger.error(f'Error processing audio message: {error}')
        await update.message.reply_text('❌ Sorry, I encountered an error processing your audio message. Please try again later.')

async def handle_document_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle document messages (audio files)"""
    document = update.message.document
    
    # Check if it's an audio file
    if document.mime_type and document.mime_type.startswith('audio/'):
        user_id = update.effective_user.id
        
        try:
            # Check rate limit
            if rate_limiter.is_rate_limited(user_id):
                time_until_reset = rate_limiter.get_time_until_reset(user_id)
                await update.message.reply_text(
                    f"⚠️ Rate limit exceeded! Please wait {int(time_until_reset / 1000)} seconds before sending another message."
                )
                return
            
            # Send typing indicator
            await context.bot.send_chat_action(chat_id=update.effective_chat.id, action="typing")
            
            # Process audio document
            transcription = await voice_service.process_voice_message(document, context.bot)
            
            # Send transcription with back button
            keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_main")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.message.reply_text(transcription, reply_markup=reply_markup)
            
        except Exception as error:
            logger.error(f'Error processing audio document: {error}')
            await update.message.reply_text('❌ Sorry, I encountered an error processing your audio file. Please try again later.')
    else:
        await update.message.reply_text('📄 I received a document, but I can only process audio files. Please send a voice message or audio file.')

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f'Update {update} caused error {context.error}')
    if update and update.message:
        await update.message.reply_text('❌ An unexpected error occurred. Please try again later.')

def main():
    """Start the bot and web server"""
    # Start Flask server in a separate thread for health checks
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    print("🌐 Web server started for health checks")
    
    # Create Telegram bot application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    
    # Add callback query handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Add message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice_message))
    application.add_handler(MessageHandler(filters.AUDIO, handle_audio_message))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document_message))
    
    # Add error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🤖 Education Bot is running!")
    print(f"Bot token: {TELEGRAM_BOT_TOKEN[:10]}...")
    print("Gemini API key configured")
    print(f"Rate limit: {RATE_LIMIT_PER_USER} messages per minute")
    print(f"Health check available at: http://localhost:{os.environ.get('PORT', 10000)}/health")
    
    # Run the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main() 
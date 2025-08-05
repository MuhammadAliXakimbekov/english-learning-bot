# 📚 Simple PDF Setup Guide

## 🎯 How to Add PDFs to Your Bot

### Step 1: Create PDF Folders
The bot expects PDF files in this structure:
```
pdfs/
├── beginner/
├── elementary/
├── pre_intermediate/
├── intermediate/
├── upper_intermediate/
└── advanced/
```

### Step 2: Add Your PDF Files
Place your PDF files in the appropriate folders:

**Beginner Level** (`pdfs/beginner/`):
- `The_Little_Prince.pdf`
- `Charlottes_Web.pdf`
- `The_Very_Hungry_Caterpillar.pdf`
- `Goodnight_Moon.pdf`
- `Where_the_Wild_Things_Are.pdf`

**Elementary Level** (`pdfs/elementary/`):
- `Matilda.pdf`
- `The_BFG.pdf`
- `Charlie_and_the_Chocolate_Factory.pdf`
- `The_Secret_Garden.pdf`
- `Little_House_on_the_Prairie.pdf`

**Pre-intermediate Level** (`pdfs/pre_intermediate/`):
- `The_Hobbit.pdf`
- `To_Kill_a_Mockingbird.pdf`
- `The_Giver.pdf`
- `Bridge_to_Terabithia.pdf`
- `The_Outsiders.pdf`

**Intermediate Level** (`pdfs/intermediate/`):
- `1984.pdf`
- `Animal_Farm.pdf`
- `The_Great_Gatsby.pdf`
- `Lord_of_the_Flies.pdf`
- `Fahrenheit_451.pdf`

**Upper-intermediate Level** (`pdfs/upper_intermediate/`):
- `Pride_and_Prejudice.pdf`
- `Jane_Eyre.pdf`
- `Wuthering_Heights.pdf`
- `Great_Expectations.pdf`
- `The_Picture_of_Dorian_Gray.pdf`

**Advanced Level** (`pdfs/advanced/`):
- `Ulysses.pdf`
- `The_Divine_Comedy.pdf`
- `War_and_Peace.pdf`
- `Don_Quixote.pdf`
- `The_Brothers_Karamazov.pdf`

### Step 3: Restart the Bot
```bash
python main.py
```

### Step 4: Test
1. Start the bot
2. Click **📖 Reading**
3. Click **📚 Digital Library**
4. Choose a level
5. Select a book
6. The bot will send the actual PDF file!

## 🎉 That's It!
Now when users select books, the bot will automatically send the actual PDF files from your local storage. No manual uploads needed!

## 📝 File Naming Rules
- Use underscores instead of spaces: `The_Little_Prince.pdf`
- Keep the exact filenames as shown above
- Make sure files are in PDF format

## 🔧 Troubleshooting
- **File not found**: Check the file path and name
- **Bot not sending PDF**: Make sure the file exists in the correct folder
- **Error sending**: Check file permissions and size

Happy teaching! 📖✨ 
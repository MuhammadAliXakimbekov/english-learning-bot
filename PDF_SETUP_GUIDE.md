# 📚 PDF Library Setup Guide

## 🎯 Overview
This guide will help you add real PDF files to your education bot's library.

## 📋 Prerequisites
1. **PDF Files**: Have your PDF books ready
2. **Chat ID**: Get your Telegram chat ID from @userinfobot
3. **Python Environment**: Make sure your bot is running

## 🚀 Step-by-Step Setup

### Step 1: Get Your Chat ID
1. Open Telegram
2. Send a message to `@userinfobot`
3. Copy your chat ID (it's a number like `123456789`)

### Step 2: Prepare Your PDF Files
1. Create a folder for your PDFs (e.g., `pdf_library/`)
2. Name your PDF files properly:
   - `The_Little_Prince.pdf`
   - `Charlotte_Web.pdf`
   - `Matilda.pdf`
   - etc.

### Step 3: Upload PDFs and Get File IDs
1. Run the upload script:
   ```bash
   python update_library.py
   ```

2. When prompted:
   - Enter your chat ID
   - Enter the path to your PDF folder

3. The script will:
   - Upload all PDFs to Telegram
   - Print the file IDs you need

### Step 4: Update the Library
1. Open `main.py`
2. Find the `LIBRARY_BOOKS` dictionary
3. Replace the placeholder file IDs with real ones:

```python
LIBRARY_BOOKS = {
    'beginner': [
        {'title': 'The Little Prince', 'author': 'Antoine de Saint-Exupéry', 'file_id': 'REAL_FILE_ID_HERE'},
        {'title': 'Charlotte\'s Web', 'author': 'E.B. White', 'file_id': 'ANOTHER_REAL_FILE_ID'},
        # ... more books
    ],
    # ... more levels
}
```

### Step 5: Test the Bot
1. Restart your bot: `python main.py`
2. Test the library feature
3. Users should now receive actual PDF files!

## 📁 File Structure Example
```
your_project/
├── main.py
├── update_library.py
├── pdf_library/
│   ├── The_Little_Prince.pdf
│   ├── Charlotte_Web.pdf
│   ├── Matilda.pdf
│   └── ...
└── ...
```

## 🔧 Troubleshooting

### Error: "Wrong remote file identifier"
- **Cause**: Using placeholder file IDs
- **Solution**: Upload real PDFs using `update_library.py`

### Error: "File not found"
- **Cause**: PDF files don't exist
- **Solution**: Check your PDF folder path

### Error: "Chat ID not found"
- **Cause**: Wrong chat ID
- **Solution**: Get your chat ID from @userinfobot

## 📚 Recommended Books by Level

### Beginner
- The Little Prince - Antoine de Saint-Exupéry
- Charlotte's Web - E.B. White
- The Very Hungry Caterpillar - Eric Carle

### Elementary
- Matilda - Roald Dahl
- Charlie and the Chocolate Factory - Roald Dahl
- The Secret Garden - Frances Hodgson Burnett

### Pre-intermediate
- The Hobbit - J.R.R. Tolkien
- To Kill a Mockingbird - Harper Lee
- The Giver - Lois Lowry

### Intermediate
- 1984 - George Orwell
- Animal Farm - George Orwell
- The Great Gatsby - F. Scott Fitzgerald

### Upper-intermediate
- Pride and Prejudice - Jane Austen
- Jane Eyre - Charlotte Brontë
- Wuthering Heights - Emily Brontë

### Advanced
- Ulysses - James Joyce
- War and Peace - Leo Tolstoy
- Don Quixote - Miguel de Cervantes

## ✅ Success Checklist
- [ ] Got chat ID from @userinfobot
- [ ] Prepared PDF files with proper names
- [ ] Ran `python update_library.py`
- [ ] Copied file IDs to `main.py`
- [ ] Restarted the bot
- [ ] Tested library feature
- [ ] Users receive actual PDF files

## 🎉 You're Done!
Your education bot now has a fully functional PDF library! Users can:
1. Choose their reading level
2. Browse available books
3. Download actual PDF files
4. Enjoy reading with AI-powered assistance

Happy teaching! 📖✨ 
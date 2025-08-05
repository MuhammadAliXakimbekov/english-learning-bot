#!/usr/bin/env python3
"""
Script to update the library with real PDF file IDs.
Run this script to upload your PDF files and get their file IDs.
"""

import asyncio
import os
from utils.pdf_uploader import PDFUploader

async def update_library():
    """Update the library with real PDF file IDs"""
    uploader = PDFUploader()
    
    # Replace with your chat ID (get this by sending a message to @userinfobot)
    chat_id = input("Enter your chat ID (get it from @userinfobot): ").strip()
    
    # Directory containing your PDF files
    pdf_directory = input("Enter the path to your PDF library directory: ").strip()
    
    if not os.path.exists(pdf_directory):
        print(f"❌ Directory not found: {pdf_directory}")
        return
    
    print(f"📚 Scanning directory: {pdf_directory}")
    
    # Upload all PDFs and get file IDs
    file_ids = await uploader.upload_multiple_pdfs(pdf_directory, chat_id)
    
    if file_ids:
        print("\n📄 File IDs for your LIBRARY_BOOKS dictionary:")
        print("=" * 50)
        
        for book_title, file_id in file_ids.items():
            print(f"'{book_title}': '{file_id}',")
        
        print("\n✅ Copy these file IDs into your main.py LIBRARY_BOOKS dictionary!")
    else:
        print("❌ No PDF files found or uploaded successfully.")

if __name__ == "__main__":
    print("📚 PDF Library Updater")
    print("=" * 30)
    print("This script will help you upload PDF files and get their file IDs.")
    print("Make sure your PDF files are named properly (e.g., 'The_Little_Prince.pdf')")
    print()
    
    asyncio.run(update_library()) 
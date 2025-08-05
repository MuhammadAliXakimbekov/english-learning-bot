import os
import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

class PDFUploader:
    def __init__(self):
        self.bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    async def upload_pdf(self, pdf_path, chat_id):
        """Upload a PDF file and return its file ID"""
        try:
            if not os.path.exists(pdf_path):
                raise FileNotFoundError(f"PDF file not found: {pdf_path}")
            
            with open(pdf_path, 'rb') as pdf_file:
                result = await self.bot.send_document(
                    chat_id=chat_id,
                    document=pdf_file,
                    caption="PDF upload test"
                )
            
            # Get the file ID from the sent document
            file_id = result.document.file_id
            print(f"✅ Successfully uploaded: {pdf_path}")
            print(f"📄 File ID: {file_id}")
            return file_id
            
        except Exception as error:
            print(f"❌ Error uploading {pdf_path}: {error}")
            return None
    
    async def upload_multiple_pdfs(self, pdf_directory, chat_id):
        """Upload all PDF files in a directory"""
        file_ids = {}
        
        if not os.path.exists(pdf_directory):
            print(f"❌ Directory not found: {pdf_directory}")
            return file_ids
        
        for filename in os.listdir(pdf_directory):
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(pdf_directory, filename)
                file_id = await self.upload_pdf(pdf_path, chat_id)
                if file_id:
                    # Extract book title from filename (remove .pdf extension)
                    book_title = filename.replace('.pdf', '').replace('_', ' ')
                    file_ids[book_title] = file_id
        
        return file_ids

async def main():
    """Example usage of PDF uploader"""
    uploader = PDFUploader()
    
    # Replace with your chat ID (you can get this by sending a message to @userinfobot)
    chat_id = "YOUR_CHAT_ID_HERE"
    
    # Upload a single PDF
    # file_id = await uploader.upload_pdf("path/to/your/book.pdf", chat_id)
    
    # Upload all PDFs in a directory
    # pdf_directory = "path/to/your/pdf/library"
    # file_ids = await uploader.upload_multiple_pdfs(pdf_directory, chat_id)
    
    # Print the file IDs to use in your LIBRARY_BOOKS dictionary
    # for book_title, file_id in file_ids.items():
    #     print(f"'{book_title}': '{file_id}',")

if __name__ == "__main__":
    asyncio.run(main()) 
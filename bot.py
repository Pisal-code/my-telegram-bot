import pytesseract
from PIL import Image
from pdf2image import convert_from_path
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Tesseract path for Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Send me a photo or a PDF and I’ll extract any Khmer or English text!")

# Handle image/photo messages
async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = await update.message.photo[-1].get_file()
    path = "photo.jpg"
    await photo.download_to_drive(path)

    img = Image.open(path)
    text = pytesseract.image_to_string(img, lang="khm+eng")

    await update.message.reply_text(text or "❌ No readable text found.")

# Handle PDF messages
async def handle_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = await update.message.document.get_file()
    path = "document.pdf"
    await file.download_to_drive(path)

    pages = convert_from_path(path, dpi=300)
    result_text = ""

    for i, page in enumerate(pages):
        text = pytesseract.image_to_string(page, lang="khm+eng")
        result_text += f"\n--- Page {i+1} ---\n{text}"

    if len(result_text) > 4000:
        with open("output.txt", "w", encoding="utf-8") as f:
            f.write(result_text)
        await update.message.reply_document(open("output.txt", "rb"))
    else:
        await update.message.reply_text(result_text or "❌ No text found in PDF.")

# Set up the bot
app = ApplicationBuilder().token("7996735646:AAFQXG7QCtHyhpq8W5kB9lEb76i2Muk77T4").build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
app.add_handler(MessageHandler(filters.Document.PDF, handle_pdf))

app.run_polling()
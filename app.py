import os
import re #regular expression
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

load_dotenv()

os.environ["LANGSMITH_API_KEY"]= os.getenv("LANGSMITH_API_KEY")
os.environ["LANGSMITH_PROJECT"]= os.getenv("LANGSMITH_PROJECT")
os.environ["LANGSMITH_TRACING"]= "true"
groq_api_key = os.getenv("GROQ_API_KEY")

def setup_llm_chain(topic="technology"):
    prompt = ChatPromptTemplate.from_messages([
        ("system","You are a professional comedy writer. Your job is to write ONE short, clever, and funny joke on any topic the user gives. Avoid cheesy or robotic lines. Make it feel natural and witty."),
        ("user",f"generate a joke on the topic: {topic}")
    ])

    llm = ChatGroq(
        model="Llama3-8b-8192",
        groq_api_key=groq_api_key
    )

    return prompt|llm|StrOutputParser()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hi! Mention me with a tpoic like '@Binary2_Joke_Bot python'to get a joke")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Mention me with a tpoic like '@Binary2_Joke_Bot python', to get some funny jokes")

async def generate_joke(update: Update, context: ContextTypes.DEFAULT_TYPE,topic: str):
    await update.message.reply_text(f"Generating a joke about {topic}")
    joke= setup_llm_chain(topic).invoke({}).strip()
    await update.message.reply_text(joke)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message.text
    bot_username = context.bot.username
    
    if f'@{bot_username}' in msg:
        match = re.search(f'@{bot_username}\\s+(.*)',msg)
        if match and match.group(1).strip():
            await generate_joke(update, context, match.group(1).strip())
        else:
            await update.message.reply_text("Please specify a topic after mentioning me")    


def main():
    token = os.getenv("TELEGRAM_API_KEY")
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
import logging
import asyncio
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager

# إعدادات التنبيهات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- الإعدادات الأساسية ---
TOKEN = '8649441814:AAFbKc37yT-eNly7Falv-UV6G6oIIwU35UA' # التوكن الخاص بك
user_data = {} # مخزن مؤقت لبيانات المستخدمين

# دالة البداية (Start)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_data[user_id] = {'step': 'email'}
    # التعديل الجديد هنا
    await update.message.reply_text("أهلاً بك في بوت الاكسلانس! 👑\n\nيرجى إرسال إيميل الفيسبوك الخاص بك:")

# دالة معالجة الرسائل واستلام البيانات
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # الحالة 1: استلام الإيميل
    if user_id in user_data and user_data[user_id].get('step') == 'email':
        user_data[user_id]['email'] = text
        user_data[user_id]['step'] = 'password'
        await update.message.reply_text("تمام يا إكسلانس، دلوقتي ابعت باسورد الفيسبوك:")
        return

    # الحالة 2: استلام الباسورد
    if user_id in user_data and user_data[user_id].get('step') == 'password':
        user_data[user_id]['password'] = text
        user_data[user_id]['step'] = 'ready'
        await update.message.reply_text("✅ تم حفظ بياناتك بنجاح!\n\nدلوقتي تقدر تنشر عن طريق إرسال:\nالمحافظة | النص\n\nمثال: القاهرة | فيلم كوميدي جديد")
        return

    # الحالة 3: تنفيذ النشر
    if user_id in user_data and user_data[user_id].get('step') == 'ready':
        if '|' in text:
            location, message = map(str.strip, text.split('|', 1))
            await update.message.reply_text(f"🔍 جاري البحث عن جروبات في {location} والنشر فيها...")
            asyncio.create_task(run_facebook_bot(update, location, message, user_data[user_id]['email'], user_data[user_id]['password']))
        else:
            await update.message.reply_text("❌ صيغة الرسالة غلط يا إكسلانس. ابعتها كدة: المحافظة | النص")

# دالة السيلينيوم للنشر
async def run_facebook_bot(update, location, post_text, email, password):
    chrome_options = Options()
    chrome_options.add_argument("--headless") 
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-notifications")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        driver.get("https://www.facebook.com/login")
        await asyncio.sleep(3)
        driver.find_element(By.ID, "email").send_keys(email)
        driver.find_element(By.ID, "pass").send_keys(password)
        driver.find_element(By.NAME, "login").click()
        await asyncio.sleep(5)

        search_url = f"https://www.facebook.com/search/groups/?q={location}"
        driver.get(search_url)
        await asyncio.sleep(5)

        await update.message.reply_text("✅ تم تسجيل الدخول وبدء النشر في الجروبات...")
        
    except Exception as e:
        await update.message.reply_text(f"❌ حصلت مشكلة: {str(e)}")
    finally:
        driver.quit()

def main():
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("البوت شغال تحت اسم 'الاكسلانس'... جرب دلوقتي!")
    application.run_polling()

if __name__ == '__main__':
    main()
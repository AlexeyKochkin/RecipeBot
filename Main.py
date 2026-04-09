from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from RecipeParser import RecipeParser

BOT_TOKEN = ''

parser = RecipeParser('recipes.txt')
parser.parse()

RECIPES_PER_PAGE = 5


def get_recipes_keyboard(page=0):
    total_recipes = len(parser.recipes)
    start_idx = page * RECIPES_PER_PAGE
    end_idx = min(start_idx + RECIPES_PER_PAGE, total_recipes)
    
    keyboard = []
    
    for i in range(start_idx, end_idx):
        recipe = parser.recipes[i]
        keyboard.append([InlineKeyboardButton(
            text=f"{recipe['id']}. {recipe['name']}",
            callback_data=f"recipe_{recipe['id']}"
        )])
    
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton(text="Назад", callback_data=f"page_{page-1}"))
    if end_idx < total_recipes:
        nav_buttons.append(InlineKeyboardButton(text="Вперед", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    return InlineKeyboardMarkup(keyboard)


def format_recipe(recipe):
    text = f"<b>{recipe['name']}</b>\n\n"
    text += f"Время приготовления: <code>{recipe['time']}</code>\n"
    text += f"Порций: <code>{recipe['portions']}</code>\n\n"
    
    if recipe['ingredients']:
        text += "<b>Ингредиенты:</b>\n"
        ingredients_lines = recipe['ingredients'].split('\n')
        for line in ingredients_lines[:15]:
            if line.strip():
                text += f"• {line.strip()}\n"
        text += "\n"
    
    if recipe['recipe']:
        text += "<b>Приготовление:</b>\n"
        recipe_lines = recipe['recipe'].split('\n')
        for line in recipe_lines[:20]:
            if line.strip():
                text += f"{line.strip()}\n"
    
    return text


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Список рецептов:",
        reply_markup=get_recipes_keyboard(0)
    )


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data.startswith("page_"):
        page = int(query.data.split("_")[1])
        await query.edit_message_text(
            "Список рецептов:",
            reply_markup=get_recipes_keyboard(page)
        )
    
    elif query.data.startswith("recipe_"):
        recipe_id = query.data.split("_")[1]
        recipe = parser.get_recipe_by_id(recipe_id)
        
        if recipe:
            text = format_recipe(recipe)
            keyboard = [[InlineKeyboardButton(text="Назад к списку", callback_data="back_0")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode='HTML'
            )
    
    elif query.data.startswith("back_"):
        page = int(query.data.split("_")[1])
        await query.edit_message_text(
            "Список рецептов:",
            reply_markup=get_recipes_keyboard(page)
        )


def main():
    application = Application.builder().token(BOT_TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    print("Бот запущен")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()

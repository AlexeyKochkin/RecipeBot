import re
from typing import List, Dict


class RecipeParser:
    
    def __init__(self, filename: str):
        self.filename = filename
        self.recipes = []
    
    def parse(self) -> List[Dict[str, str]]:
        with open(self.filename, 'r', encoding='utf-8') as f:
            content = f.read()
        
        recipe_pattern = r'(?:\t)?(\d+)\.\s+(.+?)(?=(?:\t)?\d+\.\s+|\Z)'
        matches = re.findall(recipe_pattern, content, re.DOTALL)
        
        for number, recipe_text in matches:
            recipe = self._parse_recipe(number, recipe_text)
            if recipe:
                self.recipes.append(recipe)
        
        return self.recipes
    
    def _parse_recipe(self, number: str, text: str) -> Dict[str, str]:
        lines = text.strip().split('\n')
        
        name = lines[0].strip() if lines else "Без названия"
        
        time_match = re.search(r'Время приготовления:\s*(.+)', text)
        portions_match = re.search(r'(\d+)\s*порци', text)
        
        ingredients = ""
        if "ИНГРЕДИЕНТЫ:" in text:
            ing_start = text.find("ИНГРЕДИЕНТЫ:")
            ing_end = text.find("РЕЦЕПТ:", ing_start)
            if ing_end > ing_start:
                ingredients = text[ing_start:ing_end].replace("ИНГРЕДИЕНТЫ:", "").strip()
        
        recipe_text = ""
        if "РЕЦЕПТ:" in text:
            rec_start = text.find("РЕЦЕПТ:")
            recipe_text = text[rec_start:].replace("РЕЦЕПТ:", "").strip()
        
        return {
            'id': number,
            'name': name,
            'time': time_match.group(1).strip() if time_match else "Не указано",
            'portions': portions_match.group(1) if portions_match else "Не указано",
            'ingredients': ingredients,
            'recipe': recipe_text,
            'full_text': text.strip()
        }
    
    def get_recipe_by_id(self, recipe_id: str) -> Dict[str, str]:
        for recipe in self.recipes:
            if recipe['id'] == recipe_id:
                return recipe
        return None
    
    def get_all_recipes_list(self) -> str:
        result = "Список рецептов:\n\n"
        for recipe in self.recipes:
            result += f"{recipe['id']}. {recipe['name']}\n"
        return result

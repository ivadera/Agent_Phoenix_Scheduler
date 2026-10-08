import json
import google.generativeai as genai
import pandas as pd
import streamlit as st

# Настройки на страницата
st.set_page_config(
    page_title="Умен Дневен График", page_icon="📅", layout="wide"
)

st.title("🤖 Умен График & Декомпозитор на Задачи")
st.write(
    "Въведете ангажиментите и задачите си, и ИИ ще изготви подреден, цветен"
    " график за деня."
)

# Извличане на защитения ключ от Secrets на Streamlit
api_key = st.secrets.get("GEMINI_API_KEY", "")

# Страничен панел
with st.sidebar:
  st.header("⚙️ Настройки")
  if api_key:
    st.success("✅ Системата е готова за работа!")
  else:
    # Запасен вариант, ако случайно не сте добавили ключа в Secrets
    api_key = st.text_input(
        "Въведете Gemini API Key:",
        type="password",
        help="Вземете безплатен ключ от Google AI Studio.",
    )

# Входни полета за потребителя
col1, col2 = st.columns(2)

with col1:
  fixed_schedule = st.text_area(
      "1. Фиксиран график / Ограничения (Работа, спорт, сън):",
      placeholder=(
          "Напр.: Работа 09:00-17:00, Обяд 12:00-13:00, Тренировка 18:00-19:00"
      ),
      height=150,
  )

with col2:
  tasks_list = st.text_area(
      "2. Задачи за разпределяне и дедлайни:",
      placeholder=(
          "Напр.: Подготовка на презентация (дедлайн утре), Плащане на сметки,"
          " Изпращане на имейл"
      ),
      height=150,
  )

generate_btn = st.button("⚡ Генерирай Умен График", type="primary")

if generate_btn:
  if not api_key:
    st.error(
        "Грешка: Липсва API ключ! Добавете го в Streamlit Secrets или в"
        " страничното меню."
    )
  elif not tasks_list:
    st.warning("Моля, въведете поне една задача!")
  else:
    try:
      genai.configure(api_key=api_key)
      model = genai.GenerativeModel("gemini-2.5-flash")

      prompt = f"""
            Ти си експерт по тайм-мениджмънт.
            Фиксиран график на потребителя: {fixed_schedule}
            Задачи за планиране: {tasks_list}

            Задача:
            1. Разбии големите задачи на по-малки стъпки (между 15 и 60 минути).
            2. Разпредели ги в свободните часове, спазвайки фиксирания график.
            3. Върни резултата САМО като валиден JSON масив от обекти със следните ключове:
               - "time": "ЧАС_НАЧАЛО - ЧАС_КРАЙ" (напр. "14:00 - 14:45")
               - "task": "Име на задачата/стъпката"
               - "category": "Категория (Работа / Лично / Спешно / Обучение)"
               - "color": "Код на цвета (Червено, Синьо, Зелено, Лилаво)"
            НЕ добавят допълнителен текст, само чист JSON!
            """

      with st.spinner("ИИ анализира задачите и изготвя графика..."):
        response = model.generate_content(prompt)
        clean_json = (
            response.text.replace("```json", "").replace("```", "").strip()
        )
        data = json.loads(clean_json)

        st.success("Графикът е готов!")

        df = pd.DataFrame(data)

        def color_rows(val):
          colors = {
              "Червено": "background-color: #ffcccc; color: black;",
              "Синьо": "background-color: #cce5ff; color: black;",
              "Зелено": "background-color: #d4edda; color: black;",
              "Лилаво": "background-color: #e2d6f5; color: black;",
          }
          return colors.get(val, "")

        st.subheader("📊 Вашият структуриран график за деня:")
        st.dataframe(
            df.style.map(color_rows, subset=["color"]), use_container_width=True
        )

    except Exception as e:
      st.error(f"Грешка при генерирането: {e}")

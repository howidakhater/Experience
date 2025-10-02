import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv

load_dotenv()

# Initialize client
client = OpenAI(
    base_url="https://router.huggingface.co/v1",
    api_key=os.getenv("HF_TOKEN"), # Replace with your actual Hugging Face token
)

st.title("Egypt Tour Planner Chatbot")

# Define the questions in different languages
travel_questions = {
    "English": [
        "What place do you want to visit in Egypt?",
        "Do you prefer to visit historical/archaeological sites or natural/marine sites?",
        "How many hours or days do you have available for the tour?",
        "Do you travel alone or with family/friends?",
        "Do you like to shop and buy souvenirs, or do you focus on visiting and taking pictures?",
        "What is your budget for the tour? Do you prefer something economical or luxury?"
    ],
    "Arabic": [
        "ما المكان الذي ترغب بزيارته في مصر؟",
        "هل تفضل زيارة المواقع التاريخية/الأثرية أم المواقع الطبيعية/البحرية؟",
        "كم عدد الساعات أو الأيام المتاحة لديك للجولة؟",
        "هل تسافر وحدك أم مع العائلة/الأصدقاء؟",
        "هل تحب التسوق وشراء الهدايا التذكارية أم تركز على الزيارة والتقاط الصور؟",
        "ما هي ميزانيتك للجولة؟ هل تفضل شيئًا اقتصاديًا أم فاخرًا؟"
    ],
    "Russian": [
        "Какое место вы хотите посетить в Египте?",
        "Вы предпочитаете посещать исторические/археологические места или природные/морские места?",
        "Сколько часов или дней у вас есть на тур?",
        "Вы путешествуете в одиночку или с семьей/друзьями?",
        "Вы любите делать покупки и покупать сувениры, или вы сосредотачиваетесь на посещении и фотографировании?",
        "Каков ваш бюджет на тур? Вы предпочитаете что-то экономичное или роскошное?"
    ],
    "German": [
        "Welchen Ort möchten Sie in Ägypten besuchen?",
        "Bevorzugen Sie historische/archäologische Stätten oder Natur-/Meeresschutzgebiete?",
        "Wie viele Stunden oder Tage stehen Ihnen für die Tour zur Verfügung?",
        "Reisen Sie alleine oder mit Familie/Freunden?",
        "Kaufen Sie gerne ein und kaufen Sie Souvenirs, oder konzentrieren Sie sich auf Besichtigungen und Fotografieren?",
        "Wie hoch ist Ihr Budget für die Tour? Bevorzugen Sie etwas Preisgünstiges oder Luxuriöses?"
    ]
}

# Define button texts in different languages
button_texts = {
    "English": {
        "next_question": "Next Question",
        "generate_itinerary": "Generate Itinerary",
        "escape_generate": "Escape and Generate Itinerary",
        "generating": "Thank you for answering the questions. Generating your personalized itinerary...",
        "suggested_itinerary": "Your Suggested Itinerary:"
    },
    "Arabic": {
        "next_question": "السؤال التالي",
        "generate_itinerary": "إنشاء خط سير الرحلة",
        "escape_generate": "تجاوز وإنشاء خط سير الرحلة",
        "generating": "شكراً لإجابتك على الأسئلة. جاري إنشاء خط سير رحلتك المخصص...",
        "suggested_itinerary": "خط سير الرحلة المقترح لك:"
    },
    "Russian": {
        "next_question": "Следующий вопрос",
        "generate_itinerary": "Сформировать маршрут",
        "escape_generate": "Пропустить и сформировать маршрут",
        "generating": "Спасибо за ответы на вопросы. Формируем ваш персональный маршрут...",
        "suggested_itinerary": "Ваш предложенный маршрут:"
    },
    "German": {
        "next_question": "Nächste Frage",
        "generate_itinerary": "Reiseroute generieren",
        "escape_generate": "Überspringen und Reiseroute generieren",
        "generating": "Vielen Dank für die Beantwortung der Fragen. Ihre personalisierte Reiseroute wird generiert...",
        "suggested_itinerary": "Ihre vorgeschlagene Reiseroute:"
    }
}


# Initialize session state for language, answers, current question index, and itinerary
if 'selected_language' not in st.session_state:
    st.session_state.selected_language = None
if 'user_answers' not in st.session_state:
    st.session_state.user_answers = {}
if 'current_question_index' not in st.session_state:
    st.session_state.current_question_index = 0
if 'itinerary' not in st.session_state:
    st.session_state.itinerary = None

def generate_itinerary(answers, language):
    """Generates a day-by-day itinerary based on user answers using a Hugging Face model."""
    # Construct the prompt
    prompt = f"Generate a day-by-day itinerary for a trip to Egypt in {language} based on the following preferences:\n\n"
    for question, answer in answers.items():
        if answer and answer.lower() != 'skip': # Include non-empty answers
            prompt += f"- {question}: {answer}\n"

    # If no answers were provided (or all were skipped), provide a default prompt
    if not any(answer and answer.lower() != 'skip' for answer in answers.values()):
        default_prompt = {
            "English": "Generate a general 3-day itinerary for visiting the highlights of Cairo, Egypt, including historical and cultural sites.",
            "Arabic": "قم بإنشاء خط سير رحلة عام لمدة 3 أيام لزيارة أبرز معالم القاهرة، مصر، بما في ذلك المواقع التاريخية والثقافية.",
            "Russian": "Создайте общий 3-дневный маршрут для посещения основных достопримечательностей Каира, Египет, включая исторические и культурные объекты.",
            "German": "Erstellen Sie eine allgemeine 3-Tages-Reiseroute für den Besuch der Highlights von Kairo, Ägypten, einschließlich historischer und kultureller Stätten."
        }
        prompt = default_prompt.get(language, default_prompt["English"]) # Default to English if language not found
    else:
        prompt += "\nPlease format the output as a clear day-by-day plan."

    # Call the Hugging Face model
    try:
        completion = client.chat.completions.create(
            model="openai/gpt-oss-20b:fireworks-ai", # Specify the model
            messages=[{"role": "user", "content": prompt}],
        )
        # Extract the generated text content
        itinerary_text = completion.choices[0].message.content
        return itinerary_text
    except Exception as e:
        st.error(f"An error occurred while generating the itinerary: {e}")
        return "Could not generate itinerary at this time."

# Display language selection if no language is selected
if st.session_state.selected_language is None:
    st.subheader("Please select your preferred language:")

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        if st.button("English 🇺🇸"):
            st.session_state.selected_language = "English"
            st.rerun()
    with col2:
        if st.button("Arabic 🇪🇬"):
            st.session_state.selected_language = "Arabic"
            st.rerun()
    with col3:
        if st.button("Russian 🇷🇺"):
            st.session_state.selected_language = "Russian"
            st.rerun()
    with col4:
        if st.button("German 🇩🇪"):
            st.session_state.selected_language = "German"
            st.rerun()

# If a language is selected, display the questions
if st.session_state.selected_language:
    st.write(f"Language selected: {st.session_state.selected_language}")
    current_questions = travel_questions[st.session_state.selected_language]
    current_button_texts = button_texts[st.session_state.selected_language]

    # Display the current question
    if st.session_state.current_question_index < len(current_questions):
        current_question = current_questions[st.session_state.current_question_index]
        user_input = st.text_input(f"{current_question}", key=f"question_{st.session_state.current_question_index}_{st.session_state.selected_language}")

        # Process the answer when user submits input
        if user_input: # Process input on every change to allow clearing or changing answers before submitting the final one
             st.session_state.user_answers[current_question] = user_input

        col_next, col_escape = st.columns(2)
        with col_next:
            if st.button(current_button_texts["next_question"] if st.session_state.current_question_index < len(current_questions) - 1 else current_button_texts["generate_itinerary"]):
                 st.session_state.current_question_index += 1
                 st.rerun()
        with col_escape:
             if st.button(current_button_texts["escape_generate"]):
                  st.session_state.current_question_index = len(current_questions) # Move to the end to trigger itinerary generation
                  st.session_state.itinerary = None # Reset itinerary to generate a new one based on current answers
                  st.rerun()


    # If all questions are answered (or escape is pressed), generate and display the itinerary
    if st.session_state.current_question_index >= len(current_questions):
        if st.session_state.itinerary is None:
            st.write(current_button_texts["generating"])
            st.session_state.itinerary = generate_itinerary(st.session_state.user_answers, st.session_state.selected_language)
            st.rerun() # Rerun to display the generated itinerary

        if st.session_state.itinerary is not None:
            st.subheader(current_button_texts["suggested_itinerary"])
            st.write(st.session_state.itinerary)









